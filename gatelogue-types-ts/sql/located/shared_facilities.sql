SELECT node1 AS i FROM SharedFacility WHERE node2 = ?1
UNION SELECT node2 AS i FROM SharedFacility WHERE node1 = ?1