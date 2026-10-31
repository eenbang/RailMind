-- Framework placeholder for the future SQLite adapter.
-- The sample adapter does not require this database yet.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    UNIQUE (name, city)
);

CREATE TABLE IF NOT EXISTS journeys (
    id TEXT PRIMARY KEY,
    train_no TEXT NOT NULL,
    departure_station_id INTEGER NOT NULL REFERENCES stations(id),
    arrival_station_id INTEGER NOT NULL REFERENCES stations(id),
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    mileage_km INTEGER NOT NULL,
    route_origin TEXT NOT NULL,
    route_terminal TEXT NOT NULL,
    train_type TEXT NOT NULL,
    data_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fares (
    journey_id TEXT NOT NULL REFERENCES journeys(id),
    seat_class TEXT NOT NULL,
    price_cny REAL NOT NULL,
    PRIMARY KEY (journey_id, seat_class)
);

CREATE INDEX IF NOT EXISTS idx_journeys_route_time
    ON journeys (departure_station_id, arrival_station_id, departure_time);

CREATE INDEX IF NOT EXISTS idx_journeys_duration
    ON journeys (duration_minutes);
