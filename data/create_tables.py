import sqlite3

con = sqlite3.connect("data/energy.db")

sql_stmt = """
create table if not exists gas
(
    time        TEXT,
    netto_costs TEXT,
    gas         REAL
);
create unique index if not exists gas_time_uindex on gas (time);

create table if not exists main_connection
(
    time        TEXT,
    netto_costs INTEGER,
    import      REAL,
    export      REAL,
    netto       REAL
);

create unique index if not exists main_connection_time_index on main_connection (time);

create table if not exists water
(
    time        TEXT,
    netto_costs TEXT,
    water       INTEGER
);

create unique index if not exists water_time_uindex on water (time);

"""

con.executescript(sql_stmt)
