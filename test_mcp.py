"""
Diagnostic: inspect ALL content blocks from MongoDB MCP Server find response.

Run: python test_mcp_connection.py
"""

from backend.mcp_client import MongoMCPClient
import json


with MongoMCPClient() as mcp:

    print("=" * 60)
    print("  MCP FIND — FULL CONTENT INSPECTION")
    print("=" * 60)

    # Submit raw find and inspect every content block
    future = mcp._submit("find", {
        "database": "smb_sentinel",
        "collection": "workflows",
        "filter": {}
    })
    result = future.result(timeout=30)

    print(f"\nTotal content blocks: {len(result.content)}")
    print(f"Result type: {type(result).__name__}")
    print(f"Result dir: {[a for a in dir(result) if not a.startswith('_')]}")

    for i, block in enumerate(result.content):
        print(f"\n--- Content Block [{i}] ---")
        print(f"  Type attr: {type(block).__name__}")
        print(f"  Dir: {[a for a in dir(block) if not a.startswith('_')]}")

        if hasattr(block, 'type'):
            print(f"  block.type: {block.type}")

        if hasattr(block, 'text'):
            text = block.text
            print(f"  text length: {len(text)}")
            print(f"  text[:300]: {text[:300]}")
            print(f"  text[-200:]: {text[-200:]}")

        if hasattr(block, 'data'):
            print(f"  Has 'data' attribute, length: {len(block.data) if block.data else 0}")

        if hasattr(block, 'resource'):
            print(f"  Has 'resource': {block.resource}")

        if hasattr(block, 'mimeType'):
            print(f"  mimeType: {block.mimeType}")

    # Also check if there's anything in isError or other fields
    print(f"\n--- Result metadata ---")
    if hasattr(result, 'isError'):
        print(f"  isError: {result.isError}")
    if hasattr(result, 'meta'):
        print(f"  meta: {result.meta}")

    # Try with limit=1 to see if smaller results include docs
    print("\n\n--- TEST: find with limit=1 ---")
    future2 = mcp._submit("find", {
        "database": "smb_sentinel",
        "collection": "workflows",
        "filter": {},
        "limit": 1
    })
    result2 = future2.result(timeout=30)
    print(f"Content blocks: {len(result2.content)}")
    for i, block in enumerate(result2.content):
        if hasattr(block, 'text'):
            print(f"  [{i}] text: {block.text[:500]}")

    # Try with projection
    print("\n\n--- TEST: find with projection ---")
    future3 = mcp._submit("find", {
        "database": "smb_sentinel",
        "collection": "workflows",
        "filter": {},
        "projection": {"workflow_id": 1, "status": 1, "customer_id": 1}
    })
    result3 = future3.result(timeout=30)
    print(f"Content blocks: {len(result3.content)}")
    for i, block in enumerate(result3.content):
        if hasattr(block, 'text'):
            print(f"  [{i}] text: {block.text[:500]}")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)
