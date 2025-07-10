-- public.os_open_map_local definition

-- Drop table
-- DROP TABLE public.os_open_map_local;

CREATE TABLE public.os_open_map_local (
	id serial4 NOT NULL,
	fid text NULL,
	gml_id text NULL,
	feature_code int4 NULL,
	geometry public.geometry(geometry, 27700) NULL,
	feature_type text NULL,
	properties jsonb NULL,
	CONSTRAINT os_open_map_local_pkey PRIMARY KEY (id)
);
CREATE INDEX os_open_map_local_feature_code_idx ON public.os_open_map_local USING btree (feature_code);
CREATE INDEX os_open_map_local_feature_type_idx ON public.os_open_map_local USING btree (feature_type);
CREATE INDEX os_open_map_local_geom_idx ON public.os_open_map_local USING gist (geometry); 