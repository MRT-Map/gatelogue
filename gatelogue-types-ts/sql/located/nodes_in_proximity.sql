SELECT node1 AS i FROM Proximity WHERE node2 = ?1
UNION SELECT node2 AS i FROM Proximity WHERE node1 = ?1