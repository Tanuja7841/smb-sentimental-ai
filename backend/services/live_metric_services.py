live_metrics = {

    "total_incidents": 0,
    "critical_incidents": 0,
    "high_risk_customers": 0,
    "revenue_at_risk": 0

}


def update_metrics(severity, revenue):

    live_metrics["total_incidents"] += 1

    if severity == "Critical":

        live_metrics["critical_incidents"] += 1

    if severity in ["High", "Critical"]:

        live_metrics["high_risk_customers"] += 1

        live_metrics["revenue_at_risk"] += revenue


def get_metrics():

    return live_metrics