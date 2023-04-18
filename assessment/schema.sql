DROP TABLE IF EXISTS weather;
DROP TABLE IF EXISTS location;

CREATE TABLE location (
	location_id TEXT NOT NULL,
    location_name TEXT NOT NULL,

    PRIMARY KEY (location_id)
);

CREATE TABLE weather (
	location_id TEXT NOT NULL,
    time_utc TEXT,
    atmospheric_pressure_mb REAL,
    wind_direction_degree INTEGER,
    wind_speed_kn REAL,
    gust_kn REAL,

    FOREIGN KEY (location_id) REFERENCES location(location_id)
);