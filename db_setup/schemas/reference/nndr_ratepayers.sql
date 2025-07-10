-- public.nndr_ratepayers definition

CREATE TABLE IF NOT EXISTS public.nndr_ratepayers (
    name TEXT,
    property_address TEXT,
    postcode TEXT,
    property_description TEXT,
    property_rateable_value_place_ref TEXT,
    liability_period_start_date DATE,
    annual_charge NUMERIC,
    exemption_amount NUMERIC,
    exemption_code TEXT,
    rateable_value NUMERIC,
    mandatory_amount NUMERIC,
    mandatory_relief TEXT,
    charity_relief_amount NUMERIC,
    disc_relief_amount NUMERIC,
    discretionary_charitable_relief TEXT,
    additional_rlf TEXT,
    additional_relief TEXT,
    sbr_applied TEXT,
    sbr_supplement TEXT,
    sbr_amount NUMERIC,
    charge_type_v_empty_commercial_property_occupied CHAR(1),
    report_date DATE
); 