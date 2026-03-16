SELECT i FROM AirGate WHERE airline = ?1
UNION SELECT "from" AS i FROM AirFlight WHERE airline = ?1
UNION SELECT "to" AS i FROM AirFlight WHERE airline = ?1