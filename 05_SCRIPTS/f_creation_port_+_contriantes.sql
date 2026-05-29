CREATE TABLE port (
    id_port INTEGER NOT NULL,
    nom_port VARCHAR(150) NOT NULL,
    nom_formel VARCHAR(200),
    code_iso2_pays CHAR(2),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    taille_port VARCHAR(50),
    type_port VARCHAR(100),
    capacite_max_navire VARCHAR(50)
);

ALTER TABLE port
    ADD CONSTRAINT pk_port
    PRIMARY KEY (id_port);

ALTER TABLE port
    ADD CONSTRAINT ck_port_latitude
    CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90);

ALTER TABLE port
    ADD CONSTRAINT ck_port_longitude
    CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180);

ALTER TABLE port
    ADD CONSTRAINT ck_port_taille
    CHECK (
        taille_port IS NULL
        OR taille_port IN ('Very Small', 'Small', 'Medium', 'Large')
    );

ALTER TABLE port
    ADD CONSTRAINT ck_port_type
    CHECK (
        type_port IS NULL
        OR type_port IN (
            'Coastal Breakwater',
            'Coastal Natural',
            'Coastal Tide Gate',
            'Lake or Canal',
            'Open Roadstead',
            'River Basin',
            'River Natural',
            'River Tide Gate'
        )
    );

ALTER TABLE port
    ADD CONSTRAINT ck_port_capacite_max
    CHECK (
        capacite_max_navire IS NULL
        OR capacite_max_navire IN ('Over 500''', 'Under 500''')
    );