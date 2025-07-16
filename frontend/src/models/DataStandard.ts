// DataStandard model for describing a data standard/metadata object

export interface DataStandard {
  name: string;
  sector: string;
  description: string;
  governing_body: string;
  jurisdictions: string[];
  version: string;
  date_issued: string;
  schema_type: string;
  file_formats: string[];
  languages_supported: string[];
  license: string;
  license_url: string;
  data_model: Array<{
    field_name: string;
    type: string;
    description: string;
    required: boolean;
  }>;
  interoperability: string;
  related_standards: string[];
  extends: string | null;
  update_frequency: string;
  validation: {
    status: string;
    score: number;
    issues: any[];
  };
  compliance: {
    regulations: string[];
    level: string;
    notes: string;
  };
  official_link: string;
  data_access_url: string;
  notes: string;
}
