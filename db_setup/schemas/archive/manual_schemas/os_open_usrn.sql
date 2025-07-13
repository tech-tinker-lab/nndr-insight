-- public.os_open_usrn definition

CREATE TABLE IF NOT EXISTS public.os_open_usrn (
    geometry public.geometry(geometryz, 27700) NULL,
    usrn int8 NULL,
    street_type text NULL
);
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_geometry ON public.os_open_usrn USING gist (geometry); 