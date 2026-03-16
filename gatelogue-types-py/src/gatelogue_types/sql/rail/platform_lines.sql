SELECT DISTINCT RailConnection.line FROM RailConnection
WHERE RailConnection."from" = ?1 OR RailConnection."to" = ?1