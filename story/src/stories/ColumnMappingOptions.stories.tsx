import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import ColumnMappingOptions from '../components/upload/ColumnMappingOptions';

const meta: Meta<typeof ColumnMappingOptions> = {
  title: 'Upload/ColumnMappingOptions',
  component: ColumnMappingOptions,
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
      description: 'Current column mappings',
      control: { type: 'object' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Wrapper component to handle state
const ColumnMappingWrapper = ({ structure, initialMapping = {} }: any) => {
  const [mapping, setMapping] = useState(initialMapping);
  
  return (
    <ColumnMappingOptions 
      structure={structure} 
      mapping={mapping} 
      setMapping={setMapping} 
    />
  );
};

export const Default: Story = {
  render: () => (
    <ColumnMappingWrapper
      structure={{
        'customer_id': { type: 'integer', sample: ['1', '2', '3', '4', '5'] },
        'customer_name': { type: 'string', sample: ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'] },
        'email': { type: 'string', sample: ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'] },
        'created_date': { type: 'string', sample: ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12'] },
        'is_active': { type: 'boolean', sample: ['true', 'false', 'true', 'true', 'false'] },
        'latitude': { type: 'float', sample: ['40.7128', '34.0522', '41.8781', '29.7604', '39.9526'] },
        'longitude': { type: 'float', sample: ['-74.0060', '-118.2437', '-87.6298', '-95.3698', '-75.1652'] },
      }}
    />
  ),
};

export const GeospatialData: Story = {
  render: () => (
    <ColumnMappingWrapper
      structure={{
        'property_id': { type: 'integer', sample: ['1001', '1002', '1003', '1004', '1005'] },
        'address': { type: 'string', sample: ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr'] },
        'geometry': { type: 'string', sample: ['POINT(-74.006 40.7128)', 'POINT(-118.2437 34.0522)', 'POINT(-87.6298 41.8781)', 'POINT(-95.3698 29.7604)', 'POINT(-75.1652 39.9526)'] },
        'lot_size_sqft': { type: 'float', sample: ['5000.5', '7500.0', '6200.25', '4800.75', '8900.0'] },
        'zoning_code': { type: 'string', sample: ['R1', 'R2', 'C1', 'R1', 'R3'] },
        'has_pool': { type: 'boolean', sample: ['false', 'true', 'false', 'false', 'true'] },
        'assessment_date': { type: 'string', sample: ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01'] },
      }}
    />
  ),
};

export const FinancialData: Story = {
  render: () => (
    <ColumnMappingWrapper
      structure={{
        'transaction_id': { type: 'integer', sample: ['10001', '10002', '10003', '10004', '10005'] },
        'account_number': { type: 'string', sample: ['ACC-001', 'ACC-002', 'ACC-003', 'ACC-004', 'ACC-005'] },
        'amount': { type: 'float', sample: ['1250.50', '2500.00', '750.25', '3200.75', '900.00'] },
        'currency': { type: 'string', sample: ['USD', 'EUR', 'GBP', 'USD', 'CAD'] },
        'transaction_date': { type: 'string', sample: ['2023-12-01', '2023-12-02', '2023-12-03', '2023-12-04', '2023-12-05'] },
        'is_verified': { type: 'boolean', sample: ['true', 'true', 'false', 'true', 'false'] },
        'merchant_location': { type: 'string', sample: ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ'] },
      }}
    />
  ),
};

export const EmptyStructure: Story = {
  render: () => (
    <ColumnMappingWrapper
      structure={{}}
    />
  ),
};
