// Table model for describing database tables and schemas

import { FieldStructure } from './FieldStructure';

export interface Table {
  name: string;
  schema: string;
  fields: FieldStructure;
  rowCount?: number;
  createdAt?: string;
  updatedAt?: string;
  // Add more fields as needed
}
