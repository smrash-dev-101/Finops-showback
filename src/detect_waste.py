import boto3
from datetime import datetime, timedelta, timezone

CPU_THRESHOLD_PERCENT = 5.0
LOOKBACK_DAYS = 7


def get_running_instances(ec2_client):
    response = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance["InstanceId"])
    return instances


def get_avg_cpu(cloudwatch_client, instance_id):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=LOOKBACK_DAYS)

    response = cloudwatch_client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=86400,
        Statistics=["Average"],
    )

    datapoints = response["Datapoints"]
    if not datapoints:
        return None

    values = [point["Average"] for point in datapoints]
    return sum(values) / len(values)


def detect_waste():
    ec2 = boto3.client("ec2", region_name="us-east-1")
    cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

    instances = get_running_instances(ec2)

    for instance_id in instances:
        avg_cpu = get_avg_cpu(cloudwatch, instance_id)

        if avg_cpu is None:
            print(f"{instance_id}: no CPU data available yet")
            continue

        flag = "WASTE CANDIDATE" if avg_cpu < CPU_THRESHOLD_PERCENT else "actively used"
        print(f"{instance_id}: avg CPU over {LOOKBACK_DAYS}d = {avg_cpu:.2f}% -> {flag}")


if __name__ == "__main__":
    detect_waste()
