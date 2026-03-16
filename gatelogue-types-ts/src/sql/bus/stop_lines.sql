SELECT DISTINCT BusConnection.line
FROM (SELECT i FROM BusBerth WHERE stop = ?1) A
LEFT JOIN BusConnection ON A.i = BusConnection."from" OR A.i = BusConnection."to"