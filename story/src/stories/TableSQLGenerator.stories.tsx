import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import TableSQLGenerator from '../components/upload/TableSQLGenerator';

const meta: Meta<typeof TableSQLGenerator> = {
  title: 'Upload/TableSQLGenerator',
  component: TableSQLGenerator,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    structure: {
      description: 'Field structure with type and sample data',
      control: { type: 'object' },
    },
    mapping: {
      description: 'Column mappings',
      control: { type: 'object' },
    },
    generatedSQL: {
      description: 'Generated SQL string',
      control: { type: 'text' },
    },
    uniqueKey: {
      description: 'Unique key for the table',
      control: { type: 'text' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Wrapper component to handle state
const TableSQLGeneratorWrapper = ({ structure, mapping, uniqueKey }: any) => {
  const [generatedSQL, setGeneratedSQL] = useState('');
  
  return (
    <TableSQLGenerator 
      structure={structure} 
      mapping={mapping}
      uniqueKey={uniqueKey}
      generatedSQL={generatedSQL}
      setGeneratedSQL={setGeneratedSQL}
    />
  );
};

export const Default: Story = {
  render: () => (
    <TableSQLGeneratorWrapper
      structure={{
        'customer_id': { type: 'integer', sample: ['1', '2', '3', '4', '5'] },
        'customer_name': { type: 'string', sample: ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'] },
        'email': { type: 'string', sample: ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'] },
        'phone': { type: 'string', sample: ['+1-555-0101', '+1-555-0102', '+1-555-0103', '+1-555-0104', '+1-555-0105'] },
        'created_date': { type: 'string', sample: ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12'] },
        'is_active': { type: 'boolean', sample: ['true', 'false', 'true', 'true', 'false'] },
      }}
      mapping={{
        'customer_id': 'id',
        'customer_name': 'name',
        'email': 'email',
        'phone': 'phone',
        'created_date': 'created_at',
        'is_active': 'active_status',
      }}
      uniqueKey="id"
    />
  ),
};

export const GeospatialTable: Story = {
  render: () => (
    <TableSQLGeneratorWrapper
      structure={{
        'property_id': { type: 'integer', sample: ['1001', '1002', '1003', '1004', '1005'] },
        'address': { type: 'string', sample: ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr'] },
        'latitude': { type: 'float', sample: ['40.7128', '34.0522', '41.8781', '29.7604', '39.9526'] },
        'longitude': { type: 'float', sample: ['-74.0060', '-118.2437', '-87.6298', '-95.3698', '-75.1652'] },
        'lot_size_sqft': { type: 'float', sample: ['5000.5', '7500.0', '6200.25', '4800.75', '8900.0'] },
        'zoning_code': { type: 'string', sample: ['R1', 'R2', 'C1', 'R1', 'R3'] },
        'has_pool': { type: 'boolean', sample: ['false', 'true', 'false', 'false', 'true'] },
        'assessment_date': { type: 'string', sample: ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01'] },
      }}
      mapping={{
        'property_id': 'id',
        'address': 'street_address',
        'latitude': 'lat',
        'longitude': 'lng',
        'lot_size_sqft': 'lot_area',
        'zoning_code': 'zone',
        'has_pool': 'pool_indicator',
        'assessment_date': 'assessed_on',
      }}
      uniqueKey="id"
    />
  ),
};

export const EmptyState: Story = {
  render: () => (
    <TableSQLGeneratorWrapper
      structure={{}}
      mapping={{}}
      uniqueKey=""
    />
  ),
};

export const FinancialTransactions: Story = {
  render: () => (
    <TableSQLGeneratorWrapper
      structure={{
        'transaction_id': { type: 'integer', sample: ['10001', '10002', '10003', '10004', '10005'] },
        'account_number': { type: 'string', sample: ['ACC-001', 'ACC-002', 'ACC-003', 'ACC-004', 'ACC-005'] },
        'amount': { type: 'float', sample: ['1250.50', '2500.00', '750.25', '3200.75', '900.00'] },
        'currency': { type: 'string', sample: ['USD', 'EUR', 'GBP', 'USD', 'CAD'] },
        'transaction_date': { type: 'string', sample: ['2023-12-01', '2023-12-02', '2023-12-03', '2023-12-04', '2023-12-05'] },
        'is_verified': { type: 'boolean', sample: ['true', 'true', 'false', 'true', 'false'] },
        'transaction_type': { type: 'string', sample: ['debit', 'credit', 'debit', 'credit', 'debit'] },
      }}
      mapping={{
        'transaction_id': 'id',
        'account_number': 'account_id',
        'amount': 'transaction_amount',
        'currency': 'currency_code',
        'transaction_date': 'processed_at',
        'is_verified': 'verified',
        'transaction_type': 'type',
      }}
      uniqueKey="id"
    />
  ),
};
