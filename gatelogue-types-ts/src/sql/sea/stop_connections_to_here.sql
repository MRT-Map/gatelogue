SELECT DISTINCT SeaConnection.i
FROM (SELECT i FROM SeaDock WHERE stop = ?1) A
INNER JOIN SeaConnection ON A.i = SeaConnection."to"