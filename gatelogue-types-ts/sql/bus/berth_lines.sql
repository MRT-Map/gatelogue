SELECT DISTINCT BusConnection.line FROM BusConnection
WHERE BusConnection."from" = ?1 OR BusConnection."to" = ?1