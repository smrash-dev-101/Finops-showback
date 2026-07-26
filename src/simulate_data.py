import random
from datetime import datetime, timedelta, timezone

TEAMS = {
    "payments-team": {"base_daily_cost": 0.40, "volatility": 0.05},
    "platform-team": {"base_daily_cost": 2.50, "volatility": 0.30},
    "data-team": {"base_daily_cost": 1.20, "volatility": 0.15},
}


def generate_daily_costs(days=30):
    end = datetime.now(timezone.utc).date()
    results = []

    for i in range(days):
        date = end - timedelta(days=(days - 1 - i))
        day_data = {"date": date.strftime("%Y-%m-%d"), "teams": {}}

        for team, profile in TEAMS.items():
            base = profile["base_daily_cost"]
            volatility = profile["volatility"]
            cost = round(random.gauss(base, volatility), 2)
            cost = max(cost, 0)
            day_data["teams"][team] = cost

        results.append(day_data)

    return results


if __name__ == "__main__":
    data = generate_daily_costs(days=7)
    for day in data:
        print(day["date"])
        for team, cost in day["teams"].items():
            print(f"  {team}: ${cost:.2f}")
