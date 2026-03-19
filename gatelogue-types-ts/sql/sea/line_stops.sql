SELECT DISTINCT SeaDock.stop
FROM (SELECT "from", "to" FROM SeaConnection WHERE line = ?1) A
LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i