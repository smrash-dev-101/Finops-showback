import boto3
from datetime import datetime, timedelta, timezone

client = boto3.client("ce", region_name="us-east-1")

end = datetime.now(timezone.utc).date()
start = end - timedelta(days=7)

response = client.get_cost_and_usage(
    TimePeriod={
        "Start": start.strftime("%Y-%m-%d"),
        "End": end.strftime("%Y-%m-%d"),
    },
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
)

for result in response["ResultsByTime"]:
    date = result["TimePeriod"]["Start"]
    cost = result["Total"]["UnblendedCost"]["Amount"]
    print(f"{date}: ${float(cost):.2f}")
