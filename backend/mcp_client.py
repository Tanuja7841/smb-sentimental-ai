"""
MCP Client for MongoDB SMB Sentinel.

Uses the OFFICIAL MongoDB MCP Server (mongodb-mcp-server) to interact
with MongoDB Atlas through the MCP protocol.

Available tools from the official server:
- find, aggregate, count
- insert-many, update-many, delete-many
- list-databases, list-collections, create-collection
- collection-schema, collection-indexes, db-stats

Setup:
    npm install -g mongodb-mcp-server

Usage:
    from backend.mcp_client import MongoMCPClient

    with MongoMCPClient() as mcp:
        mcp.save_workflow("wf_123", "c1")
        mcp.save_agent_memory(...)
"""

import asyncio
import json
import os
import re
import shutil
import threading
from pathlib import Path
from concurrent.futures import Future
from dotenv import load_dotenv
from datetime import datetime

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Regex to extract data from MCP security boundary tags
UNTRUSTED_DATA_PATTERN = re.compile(
    r'<untrusted-user-data-[^>]+>(.*?)</untrusted-user-data-[^>]+>',
    re.DOTALL
)


class MongoMCPClient:
    """
    Connects to the official MongoDB MCP Server via stdio transport.
    Maintains a PERSISTENT session in a background thread.

    The official MongoDB MCP server returns responses in two content blocks:
      content[0] = summary text ("Found N documents...")
      content[1] = actual data wrapped in <untrusted-user-data-UUID> tags

    This client extracts the JSON from those security boundary tags.
    """

    DATABASE = "smb_sentinel"
    MAX_RETRIES = 2

    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")

        if not self.mongo_uri:
            raise ValueError("MONGO_URI is not set in the .env file.")

        server_env = os.environ.copy()
        server_env["MDB_MCP_CONNECTION_STRING"] = self.mongo_uri

        # Find the mongodb-mcp-server binary
        installed_server = shutil.which("mongodb-mcp-server")

        # Wrap in sh -c to suppress Node.js stderr noise (EPIPE on shutdown)
        if installed_server:
            server_cmd = installed_server
        else:
            server_cmd = "npx -y mongodb-mcp-server"

        self.server_params = StdioServerParameters(
            command="sh",
            args=["-c", f"{server_cmd} 2>/dev/null"],
            env=server_env
        )

        # Background thread state
        self._loop = None
        self._call_queue = None
        self._thread = None
        self._ready = threading.Event()
        self._running = False
        self._lock = threading.Lock()

    def connect(self):
        """Start the MCP server in a background thread."""
        with self._lock:
            if self._running:
                return
            self._ready.clear()
            self._loop = asyncio.new_event_loop()
            self._call_queue = asyncio.Queue()
            self._running = True
            self._thread = threading.Thread(
                target=self._run_loop, daemon=True
            )
            self._thread.start()
            if not self._ready.wait(timeout=30):
                self._running = False
                raise TimeoutError("MongoDB MCP Server failed to start within 30s")

    def _run_loop(self):
        """Background thread: run the async session loop."""
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._session_loop())
        except BaseException:
            pass
        finally:
            self._running = False

    async def _session_loop(self):
        """
        Single async task that owns the entire MCP session lifecycle.
        All tool calls are dispatched through the queue.
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self._ready.set()

                while self._running:
                    try:
                        item = await asyncio.wait_for(
                            self._call_queue.get(), timeout=0.5
                        )
                    except asyncio.TimeoutError:
                        continue

                    if item is None:
                        break

                    future, method, args = item

                    try:
                        if method == "list_tools":
                            result = await session.list_tools()
                            future.set_result(result)
                        else:
                            result = await session.call_tool(method, args)
                            future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)

    def _reconnect(self):
        """Force close and reconnect the MCP server."""
        with self._lock:
            self._running = False
            if self._loop and self._call_queue:
                try:
                    self._loop.call_soon_threadsafe(
                        self._call_queue.put_nowait, None
                    )
                except Exception:
                    pass
            if self._thread:
                self._thread.join(timeout=5)

            self._ready.clear()
            self._loop = asyncio.new_event_loop()
            self._call_queue = asyncio.Queue()
            self._running = True
            self._thread = threading.Thread(
                target=self._run_loop, daemon=True
            )
            self._thread.start()
            if not self._ready.wait(timeout=30):
                self._running = False
                raise TimeoutError("MongoDB MCP Server reconnection failed")

    def close(self):
        """Shut down the MCP server."""
        if not self._running:
            return
        self._running = False
        if self._loop and self._call_queue:
            try:
                self._loop.call_soon_threadsafe(
                    self._call_queue.put_nowait, None
                )
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=10)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def _submit(self, method: str, arguments: dict = None) -> Future:
        """Submit a call to the background session."""
        if not self._running:
            self.connect()
        future = Future()
        self._loop.call_soon_threadsafe(
            self._call_queue.put_nowait,
            (future, method, arguments or {})
        )
        return future

    def _extract_json_from_content(self, content_blocks) -> any:
        """
        Extract JSON data from MCP response content blocks.

        The official MongoDB MCP server returns:
          content[0] = summary text ("Query resulted in N documents...")
          content[1] = data wrapped in <untrusted-user-data-UUID>...</untrusted-user-data-UUID>

        This method checks ALL content blocks and extracts the JSON.
        """
        for block in content_blocks:
            if not hasattr(block, 'text'):
                continue

            text = block.text

            # Try direct JSON parse first (for simple responses like insert results)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, ValueError):
                pass

            # Extract from <untrusted-user-data-UUID> security boundary tags
            match = UNTRUSTED_DATA_PATTERN.search(text)
            if match:
                inner = match.group(1).strip()
                try:
                    return json.loads(inner)
                except (json.JSONDecodeError, ValueError):
                    pass

            # Try to find JSON array in plain text
            if '[' in text:
                array_match = re.search(r'\[.*\]', text, re.DOTALL)
                if array_match:
                    try:
                        return json.loads(array_match.group())
                    except (json.JSONDecodeError, ValueError):
                        pass

        # Nothing parseable found — return summary text from first block
        if content_blocks and hasattr(content_blocks[0], 'text'):
            return {"raw_response": content_blocks[0].text}

        return {"status": "no_content"}

    def call_tool(self, tool_name: str, arguments: dict):
        """
        Call an MCP tool with auto-reconnect on failure.
        Parses response from ALL content blocks.
        """
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                future = self._submit(tool_name, arguments)
                result = future.result(timeout=30)

                if result.content and len(result.content) > 0:
                    return self._extract_json_from_content(result.content)

                return {"status": "no_content"}

            except Exception as e:
                error_str = str(e).lower()
                is_connection_error = any(keyword in error_str for keyword in [
                    "epipe", "broken pipe", "connection reset",
                    "broken resource", "closed", "eof",
                    "stream", "transport"
                ])

                if is_connection_error and attempt < self.MAX_RETRIES:
                    print(f"  [MCP] Connection lost — reconnecting (attempt {attempt + 1})...")
                    try:
                        self._reconnect()
                    except Exception:
                        pass
                    continue
                else:
                    print(f"  [MCP] Error: {str(e)[:100]}")
                    return {"error": str(e), "raw_response": ""}

    def _find_documents(self, collection: str, filter: dict = None, sort: dict = None, limit: int = None) -> list:
        """
        Execute a find query and ALWAYS return a list of documents.
        """
        args = {
            "database": self.DATABASE,
            "collection": collection,
            "filter": filter or {}
        }
        if sort:
            args["sort"] = sort
        if limit:
            args["limit"] = limit

        result = self.call_tool("find", args)

        # Already a list — perfect
        if isinstance(result, list):
            return result

        # Dict response — try to extract documents
        if isinstance(result, dict):
            if "error" in result or "raw_response" in result:
                return []
            for key in ["documents", "result", "results", "data", "cursor"]:
                if key in result:
                    val = result[key]
                    if isinstance(val, list):
                        return val
                    if isinstance(val, dict) and "firstBatch" in val:
                        return val["firstBatch"]
            if "_id" in result or "workflow_id" in result:
                return [result]

        return []

    def list_tools(self) -> list:
        """List all available tools from the MongoDB MCP Server."""
        future = self._submit("list_tools")
        result = future.result(timeout=30)
        return [
            {"name": t.name, "description": t.description}
            for t in result.tools
        ]

    # ==========================================================
    # CONVENIENCE METHODS
    # ==========================================================

    def save_workflow(self, workflow_id: str, customer_id: str):
        """Insert a new workflow document."""
        return self.call_tool("insert-many", {
            "database": self.DATABASE,
            "collection": "workflows",
            "documents": [{
                "workflow_id": workflow_id,
                "customer_id": customer_id,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }]
        })

    def complete_workflow(self, workflow_id: str):
        """Mark a workflow as completed."""
        return self.call_tool("update-many", {
            "database": self.DATABASE,
            "collection": "workflows",
            "filter": {"workflow_id": workflow_id},
            "update": {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                }
            }
        })

    def get_workflows(self):
        """Get all workflows."""
        return self._find_documents("workflows", sort={"created_at": -1}, limit=100)

    def save_agent_memory(
        self,
        workflow_id: str,
        customer_id: str,
        agent_name: str,
        finding
    ):
        """Save an agent's finding to memory."""
        finding_data = finding if isinstance(finding, dict) else json.loads(finding) if isinstance(finding, str) else str(finding)
        return self.call_tool("insert-many", {
            "database": self.DATABASE,
            "collection": "agent_memory",
            "documents": [{
                "workflow_id": workflow_id,
                "customer_id": customer_id,
                "agent_name": agent_name,
                "finding": finding_data,
                "timestamp": datetime.utcnow().isoformat()
            }]
        })

    def get_customer_context(self, workflow_id: str, customer_id: str):
        """Get all agent findings for a customer in a workflow."""
        return self._find_documents(
            "agent_memory",
            filter={"workflow_id": workflow_id, "customer_id": customer_id},
            sort={"timestamp": 1}
        )

    def get_customer_memory(self, customer_id: str):
        """Get all historical memory for a customer."""
        return self._find_documents(
            "agent_memory",
            filter={"customer_id": customer_id}
        )

    def load_memory(self):
        """Load all agent memory records."""
        return self._find_documents("agent_memory", limit=100)

    def save_supervisor_decision(
        self,
        workflow_id: str,
        customer_id: str,
        selected_agents: list
    ):
        """Save the supervisor agent's routing decision."""
        return self.call_tool("insert-many", {
            "database": self.DATABASE,
            "collection": "agent_memory",
            "documents": [{
                "workflow_id": workflow_id,
                "customer_id": customer_id,
                "agent_name": "supervisor_agent",
                "finding": {"selected_agents": selected_agents},
                "timestamp": datetime.utcnow().isoformat()
            }]
        })

    def create_task(
        self,
        workflow_id: str,
        assigned_agent: str,
        task_type: str,
        task_details
    ):
        """Create a task for an agent."""
        details = task_details if isinstance(task_details, dict) else json.loads(task_details) if isinstance(task_details, str) else {}
        return self.call_tool("insert-many", {
            "database": self.DATABASE,
            "collection": "agent_tasks",
            "documents": [{
                "workflow_id": workflow_id,
                "assigned_agent": assigned_agent,
                "task_type": task_type,
                "task_details": details,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }]
        })

    def get_tasks_for_agent(self, workflow_id: str, agent_name: str):
        """Get pending tasks assigned to an agent."""
        return self._find_documents(
            "agent_tasks",
            filter={
                "workflow_id": workflow_id,
                "assigned_agent": agent_name,
                "status": "pending"
            }
        )

    def complete_task(self, workflow_id: str, agent_name: str = "recovery_agent"):
        """
        Mark tasks as completed using workflow_id + agent filter.
        (Cannot use _id directly because BSON ObjectId format doesn't match through MCP)
        """
        return self.call_tool("update-many", {
            "database": self.DATABASE,
            "collection": "agent_tasks",
            "filter": {
                "workflow_id": workflow_id,
                "assigned_agent": agent_name,
                "status": "pending"
            },
            "update": {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                }
            }
        })

    def get_agent_tasks(self):
        """Get all agent tasks."""
        return self._find_documents("agent_tasks", sort={"created_at": -1}, limit=100)

    def send_agent_message(
        self,
        workflow_id: str,
        from_agent: str,
        to_agent: str,
        message: str
    ):
        """Send a message from one agent to another."""
        return self.call_tool("insert-many", {
            "database": self.DATABASE,
            "collection": "agent_messages",
            "documents": [{
                "workflow_id": workflow_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": message,
                "created_at": datetime.utcnow().isoformat()
            }]
        })

    def get_agent_messages(self, workflow_id: str = "", agent_name: str = ""):
        """Get agent messages, optionally filtered."""
        query = {}
        if workflow_id:
            query["workflow_id"] = workflow_id
        if agent_name:
            query["from_agent"] = agent_name

        return self._find_documents(
            "agent_messages",
            filter=query,
            sort={"created_at": 1},
            limit=100
        )

    def upsert_customer_profile(
        self,
        customer_id: str,
        customer_name: str,
        churn_score: int = 0,
        risk_level: str = "",
        root_cause: str = "",
        recovery_strategy: str = ""
    ):
        """Create or update a customer profile (upsert)."""
        update_fields = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "updated_at": datetime.utcnow().isoformat()
        }
        if churn_score:
            update_fields["last_churn_score"] = churn_score
        if risk_level:
            update_fields["last_risk_level"] = risk_level
        if root_cause:
            update_fields["last_root_cause"] = root_cause
        if recovery_strategy:
            update_fields["last_recovery_strategy"] = recovery_strategy

        return self.call_tool("update-many", {
            "database": self.DATABASE,
            "collection": "customer_profiles",
            "filter": {"customer_id": customer_id},
            "update": {
                "$set": update_fields,
                "$inc": {"incident_count": 1}
            },
            "upsert": True
        })

    def get_customer_profile(self, customer_id: str):
        """Get a customer's profile."""
        return self._find_documents(
            "customer_profiles",
            filter={"customer_id": customer_id}
        )

    def get_all_customer_profiles(self):
        """Get all customer profiles."""
        return self._find_documents("customer_profiles", limit=100)

    def get_workflow_timeline(self, workflow_id: str):
        """Get the full timeline of agent actions in a workflow."""
        return self._find_documents(
            "agent_memory",
            filter={"workflow_id": workflow_id},
            sort={"timestamp": 1}
        )

    def get_latest_executive_brief(self):
        """Get the most recent executive agent brief."""
        return self._find_documents(
            "agent_memory",
            filter={"agent_name": "executive_agent"},
            sort={"timestamp": -1},
            limit=1
        )
