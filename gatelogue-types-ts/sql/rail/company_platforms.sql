SELECT DISTINCT RailPlatform.i
FROM (SELECT i FROM RailStation WHERE company = ?1) A
INNER JOIN RailPlatform on A.i = RailPlatform.station