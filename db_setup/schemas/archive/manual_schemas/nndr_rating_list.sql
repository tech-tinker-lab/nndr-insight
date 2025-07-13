-- public.nndr_rating_list definition

CREATE TABLE IF NOT EXISTS public.nndr_rating_list (
    list_altered DATE,
    community_code INTEGER,
    ba_reference TEXT,
    property_category_code TEXT,
    property_description TEXT,
    property_address TEXT,
    street_descriptor TEXT,
    locality TEXT,
    post_town TEXT,
    administrative_area TEXT,
    postcode TEXT,
    effective_date DATE,
    partially_domestic_signal CHAR(1),
    rateable_value NUMERIC,
    scat_code TEXT,
    appeal_settlement_code TEXT,
    unique_property_ref TEXT
); 