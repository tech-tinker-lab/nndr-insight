-- public.onspd definition

CREATE TABLE IF NOT EXISTS public.onspd (
    pcds text NOT NULL,
    pcd text NULL,
    lat numeric(10, 6) NULL,
    long numeric(10, 6) NULL,
    ctry text NULL,
    oslaua text NULL,
    osward text NULL,
    parish text NULL,
    oa11 text NULL,
    lsoa11 text NULL,
    msoa11 text NULL,
    imd text NULL,
    rgn text NULL,
    pcon text NULL,
    ur01ind text NULL,
    oac11 text NULL,
    oseast1m text NULL,
    osnrth1m text NULL,
    dointr text NULL,
    doterm text NULL,
    CONSTRAINT onspd_pkey PRIMARY KEY (pcds)
);
CREATE INDEX IF NOT EXISTS idx_onspd_admin ON public.onspd (oslaua);
CREATE INDEX IF NOT EXISTS idx_onspd_coords ON public.onspd (lat, long);
CREATE INDEX IF NOT EXISTS idx_onspd_country ON public.onspd (ctry);
CREATE INDEX IF NOT EXISTS idx_onspd_oa ON public.onspd (oa11); 