SELECT DISTINCT SeaConnection.line FROM SeaConnection
WHERE SeaConnection."from" = ?1 OR SeaConnection."to" = ?1