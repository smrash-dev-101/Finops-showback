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
    GroupBy=[
        {"Type": "TAG", "Key": "team"}
    ],
)

for result in response["ResultsByTime"]:
    date = result["TimePeriod"]["Start"]
    print(f"\n{date}:")
    for group in result["Groups"]:
        team_tag = group["Keys"][0]
        cost = group["Metrics"]["UnblendedCost"]["Amount"]
        print(f"  {team_tag}: ${float(cost):.2f}")
