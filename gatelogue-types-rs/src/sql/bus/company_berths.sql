SELECT DISTINCT BusBerth.i
FROM (SELECT i FROM BusStop WHERE company = ?1) A
INNER JOIN BusBerth on A.i = BusBerth.stop