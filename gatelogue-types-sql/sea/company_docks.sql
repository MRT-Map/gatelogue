SELECT DISTINCT SeaDock.i
FROM (SELECT i FROM SeaStop WHERE company = ?1) A
INNER JOIN SeaDock on A.i = SeaDock.stop