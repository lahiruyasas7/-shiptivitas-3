-- TYPE YOUR SQL QUERY BELOW

-- PART 1: Create a SQL query that maps out the daily average users before and after the feature change

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

-- PART 2: Create a SQL query that indicates the number of status changes by card

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

