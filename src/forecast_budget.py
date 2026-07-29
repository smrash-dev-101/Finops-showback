from datetime import datetime, timezone
import calendar
from simulate_data import generate_daily_costs

BUDGETS = {
    "payments-team": 15.00,
    "platform-team": 90.00,
    "data-team": 45.00,
}


def forecast(days_history=7):
    today = datetime.now(timezone.utc).date()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    day_of_month = today.day
    days_remaining = days_in_month - day_of_month

    data = generate_daily_costs(days=days_history)
    teams = data[0]["teams"].keys()

    for team in teams:
        recent_costs = [day["teams"][team] for day in data]
        avg_daily = sum(recent_costs) / len(recent_costs)

        spent_so_far = avg_daily * day_of_month
        projected_remaining = avg_daily * days_remaining
        projected_total = spent_so_far + projected_remaining

        budget = BUDGETS[team]
        status = "OVER BUDGET" if projected_total > budget else "on track"

        print(f"{team}: avg/day=${avg_daily:.2f}, projected month total=${projected_total:.2f}, budget=${budget:.2f} -> {status}")


if __name__ == "__main__":
    forecast()
