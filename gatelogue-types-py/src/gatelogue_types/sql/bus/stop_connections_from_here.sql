SELECT DISTINCT BusConnection.i
FROM (SELECT i FROM BusBerth WHERE stop = ?1) A
INNER JOIN BusConnection ON A.i = BusConnection."from"