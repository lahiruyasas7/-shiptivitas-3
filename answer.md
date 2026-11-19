# Shiptivitas Analytics SQL

## 1. Daily average users before and after the Kanban Board release

```sql
WITH daily_users AS (
    SELECT
        date(login_timestamp, 'unixepoch') AS login_date,
        count(DISTINCT user_id) AS daily_active_users
    FROM login_history
    GROUP BY date(login_timestamp, 'unixepoch')
)
SELECT
    CASE
        WHEN login_date < '2018-06-02' THEN 'Before Kanban Board'
        ELSE 'After Kanban Board'
    END AS release_period,
    avg(daily_active_users) AS daily_average_users
FROM daily_users
GROUP BY release_period;
```

The release boundary is `2018-06-02`.

## 2. Status changes by card

```sql
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
ORDER BY status_change_count DESC, c.id;
```

Initial backlog creation records are excluded because `oldStatus` is `NULL`. The query therefore counts only actual status transitions.
