import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "shiptivity.db"
OUTPUT_DIR = ROOT / "graphs"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_data():
    connection = sqlite3.connect(DATABASE)

    daily_average = connection.execute(
        """
        WITH daily_users AS (
            SELECT
                date(login_timestamp, 'unixepoch') AS login_date,
                count(DISTINCT user_id) AS daily_active_users
            FROM login_history
            GROUP BY date(login_timestamp, 'unixepoch')
        )
        SELECT
            CASE
                WHEN login_date < '2018-06-02' THEN 'Before'
                ELSE 'After'
            END AS release_period,
            avg(daily_active_users) AS daily_average_users
        FROM daily_users
        GROUP BY release_period
        """
    ).fetchall()

    card_changes = connection.execute(
        """
        SELECT
            c.id AS card_id,
            c.name AS card_name,
            count(h.id) AS status_change_count
        FROM card AS c
        LEFT JOIN card_change_history AS h
            ON h.cardID = c.id
            AND h.oldStatus IS NOT NULL
            AND h.oldStatus != h.newStatus
        GROUP BY c.id, c.name
        ORDER BY c.id
        """
    ).fetchall()

    connection.close()
    return daily_average, card_changes


def create_daily_average_chart(daily_average):
    period_order = ["Before", "After"]
    values = {
        period: average
        for period, average in daily_average
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        period_order,
        [values["Before"], values["After"]],
        color=["#6baed6", "#fd8d3c"],
    )
    ax.set_title("Daily Average Users Before and After Kanban Board Release")
    ax.set_ylabel("Daily active users")
    ax.set_xlabel("2018-06-02 release boundary")
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, period in zip(bars, period_order):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{bar.get_height():.2f}",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "daily_average_users.png", dpi=150)
    plt.close(fig)


def create_card_changes_chart(card_changes):
    card_ids = [row[0] for row in card_changes]
    change_counts = [row[2] for row in card_changes]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(card_ids, change_counts, marker="o", linewidth=1, markersize=3)
    ax.set_title("Status Changes by Card")
    ax.set_xlabel("Card ID")
    ax.set_ylabel("Status change count")
    ax.set_xlim(1, 200)
    ax.set_xticks(range(1, 201, 10))
    ax.grid(linestyle="--", alpha=0.35)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "status_changes_by_card.png", dpi=150)
    plt.close(fig)


def main():
    daily_average, card_changes = get_data()
    create_daily_average_chart(daily_average)
    create_card_changes_chart(card_changes)

    print("Created:")
    print(OUTPUT_DIR / "daily_average_users.png")
    print(OUTPUT_DIR / "status_changes_by_card.png")


if __name__ == "__main__":
    main()
