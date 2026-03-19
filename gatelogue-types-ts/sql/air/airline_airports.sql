SELECT DISTINCT airport FROM AirGate WHERE airline = ?1
UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = "from" WHERE AirFlight.airline = ?1
UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = "to" WHERE AirFlight.airline = ?1