SELECT DISTINCT SeaConnection.line
FROM (SELECT i FROM SeaDock WHERE stop = ?1) A
LEFT JOIN SeaConnection ON A.i = SeaConnection."from" OR A.i = SeaConnection."to"