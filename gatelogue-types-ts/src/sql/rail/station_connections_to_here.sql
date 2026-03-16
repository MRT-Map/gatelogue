SELECT DISTINCT RailConnection.i
FROM (SELECT i FROM RailPlatform WHERE station = ?1) A
INNER JOIN RailConnection ON A.i = RailConnection."to"