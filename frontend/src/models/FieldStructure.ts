// Field structure model for data ingestion, mapping, and SQL generation


export enum FieldType {
  TEXT = 'TEXT',
  INTEGER = 'INTEGER',
  FLOAT = 'FLOAT',
  DATE = 'DATE',
  BOOLEAN = 'BOOLEAN',
  GEOMETRY = 'GEOMETRY',
  POINT = 'POINT',
  LINESTRING = 'LINESTRING',
  POLYGON = 'POLYGON',
  MULTIPOINT = 'MULTIPOINT',
  MULTILINESTRING = 'MULTILINESTRING',
  MULTIPOLYGON = 'MULTIPOLYGON',
  JSON = 'JSON',
  UUID = 'UUID',
  SERIAL = 'SERIAL',
  BIGINT = 'BIGINT',
  SMALLINT = 'SMALLINT',
  TIMESTAMP = 'TIMESTAMP',
  TIME = 'TIME',
  DATEONLY = 'DATEONLY',
  ARRAY = 'ARRAY',
  ENUM = 'ENUM',
  BLOB = 'BLOB',
  CITEXT = 'CITEXT',
  TSVECTOR = 'TSVECTOR',
  HSTORE = 'HSTORE',
  RANGE = 'RANGE',
  OTHER = 'OTHER',
}

export interface FieldStructure {
  [fieldName: string]: FieldType;
}

// Analysis object model (FileAnalysis)
export interface FileAnalysis {
  filename: string;
  format: string;
  headers: string[];
  structure: FieldStructure;
  sampleRows?: string[][];
  // Add more fields as needed for your analysis output
}
