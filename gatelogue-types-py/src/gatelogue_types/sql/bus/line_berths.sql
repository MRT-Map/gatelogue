SELECT DISTINCT BusBerth.i
FROM (SELECT "from", "to" FROM BusConnection WHERE line = ?1) A
LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i