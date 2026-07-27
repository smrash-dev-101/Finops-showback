import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from simulate_data import generate_daily_costs

OUTPUT_DIR = "dashboard"


def build_chart(data):
    dates = [day["date"] for day in data]
    teams = data[0]["teams"].keys()

    plt.figure(figsize=(10, 5))

    for team in teams:
        costs = [day["teams"][team] for day in data]
        plt.plot(dates, costs, marker="o", label=team)

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Daily cost (USD)")
    plt.title("Team spend, last 14 days")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/cost_chart.png")
    plt.close()


def build_html():
    html = """<!DOCTYPE html>
<html>
<head><title>FinOps Showback Dashboard</title></head>
<body style="font-family: sans-serif; max-width: 900px; margin: 40px auto;">
<h1>FinOps Showback Dashboard</h1>
<p>Daily spend by team, based on the last 14 days.</p>
<img src="cost_chart.png" style="max-width: 100%;">
</body>
</html>"""
    with open(f"{OUTPUT_DIR}/index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = generate_daily_costs(days=14)
    build_chart(data)
    build_html()
    print(f"Dashboard written to {OUTPUT_DIR}/index.html")
