SELECT DISTINCT RailConnection.line
FROM (SELECT i FROM RailPlatform WHERE station = ?1) A
LEFT JOIN RailConnection ON A.i = RailConnection."from" OR A.i = RailConnection."to"