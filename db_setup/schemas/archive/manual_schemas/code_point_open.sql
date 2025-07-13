-- public.code_point_open definition

CREATE TABLE IF NOT EXISTS public.code_point_open (
    postcode text NOT NULL,
    positional_quality_indicator int4 NULL,
    easting numeric(10, 3) NULL,
    northing numeric(10, 3) NULL,
    country_code varchar(20) NULL,
    nhs_regional_ha_code varchar(20) NULL,
    nhs_ha_code varchar(20) NULL,
    admin_county_code varchar(20) NULL,
    admin_district_code varchar(20) NULL,
    admin_ward_code varchar(20) NULL,
    CONSTRAINT code_point_open_pkey PRIMARY KEY (postcode)
);
CREATE INDEX IF NOT EXISTS idx_code_point_open_admin ON public.code_point_open (admin_district_code);
CREATE INDEX IF NOT EXISTS idx_code_point_open_coords ON public.code_point_open (easting, northing);
CREATE INDEX IF NOT EXISTS idx_code_point_open_country ON public.code_point_open (country_code); 