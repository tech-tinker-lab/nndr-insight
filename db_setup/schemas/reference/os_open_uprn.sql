-- public.os_open_uprn definition

CREATE TABLE IF NOT EXISTS public.os_open_uprn (
    uprn int8 NOT NULL,
    x_coordinate numeric(10, 3) NULL,
    y_coordinate numeric(10, 3) NULL,
    latitude numeric(10, 8) NULL,
    longitude numeric(11, 8) NULL,
    CONSTRAINT os_open_uprn_pkey PRIMARY KEY (uprn)
);
CREATE INDEX IF NOT EXISTS idx_os_open_uprn_coords ON public.os_open_uprn (x_coordinate, y_coordinate);
CREATE INDEX IF NOT EXISTS idx_os_open_uprn_latlong ON public.os_open_uprn (latitude, longitude); 