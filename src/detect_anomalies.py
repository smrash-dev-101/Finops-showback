import statistics
from simulate_data import generate_daily_costs

Z_SCORE_THRESHOLD = 2.0


def detect_anomalies(days=14):
    data = generate_daily_costs(days=days)

    all_teams = data[0]["teams"].keys()

    for team in all_teams:
        history = [day["teams"][team] for day in data[:-1]]
        today = data[-1]["teams"][team]

        avg = statistics.mean(history)
        stdev = statistics.stdev(history)

        if stdev == 0:
            continue

        z_score = (today - avg) / stdev

        flag = "ANOMALY" if abs(z_score) > Z_SCORE_THRESHOLD else "normal"
        print(f"{team}: today=${today:.2f}, avg=${avg:.2f}, stdev=${stdev:.2f}, z={z_score:.2f} -> {flag}")


if __name__ == "__main__":
    detect_anomalies()
