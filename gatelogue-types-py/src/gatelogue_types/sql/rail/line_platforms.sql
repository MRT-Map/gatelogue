SELECT DISTINCT RailPlatform.i
FROM (SELECT "from", "to" FROM RailConnection WHERE line = ?1) A
LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i