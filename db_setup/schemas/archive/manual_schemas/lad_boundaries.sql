-- public.lad_boundaries definition

CREATE TABLE IF NOT EXISTS public.lad_boundaries (
    lad25cd TEXT,
    lad25nm TEXT,
    lad25nmw TEXT,
    bng_e DOUBLE PRECISION,
    bng_n DOUBLE PRECISION,
    long DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    globalid TEXT,
    geometry geometry(GEOMETRY, 27700)
); 