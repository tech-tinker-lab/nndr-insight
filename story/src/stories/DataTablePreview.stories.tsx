import type { Meta, StoryObj } from '@storybook/react';
import DataTablePreview from '../components/upload/DataTablePreview';

const meta: Meta<typeof DataTablePreview> = {
  title: 'Upload/DataTablePreview',
  component: DataTablePreview,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    preview: {
      description: 'Preview data with headers and rows',
      control: { type: 'object' },
    },
    showMappingOptions: {
      description: 'Whether to show column mapping indicators',
      control: { type: 'boolean' },
    },
    columnMappings: {
      description: 'Column mappings (optional)',
      control: { type: 'object' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    preview: {
      headers: ['customer_id', 'customer_name', 'email', 'phone', 'created_date', 'is_active'],
      data: [
        ['1', 'John Doe', 'john@example.com', '+1-555-0101', '2023-01-15', 'true'],
        ['2', 'Jane Smith', 'jane@example.com', '+1-555-0102', '2023-02-20', 'false'],
        ['3', 'Bob Johnson', 'bob@example.com', '+1-555-0103', '2023-03-10', 'true'],
        ['4', 'Alice Brown', 'alice@example.com', '+1-555-0104', '2023-04-05', 'true'],
        ['5', 'Charlie Wilson', 'charlie@example.com', '+1-555-0105', '2023-05-12', 'false'],
      ],
    },
  },
};

export const WithMapping: Story = {
  args: {
    preview: {
      headers: ['customer_id', 'customer_name', 'email', 'phone', 'created_date', 'is_active'],
      data: [
        ['1', 'John Doe', 'john@example.com', '+1-555-0101', '2023-01-15', 'true'],
        ['2', 'Jane Smith', 'jane@example.com', '+1-555-0102', '2023-02-20', 'false'],
        ['3', 'Bob Johnson', 'bob@example.com', '+1-555-0103', '2023-03-10', 'true'],
        ['4', 'Alice Brown', 'alice@example.com', '+1-555-0104', '2023-04-05', 'true'],
        ['5', 'Charlie Wilson', 'charlie@example.com', '+1-555-0105', '2023-05-12', 'false'],
      ],
    },
    showMappingOptions: true,
    columnMappings: {
      'customer_id': 'id',
      'customer_name': 'name',
      'email': 'email_address',
      'phone': 'phone_number',
      'created_date': 'created_at',
      'is_active': 'active_status',
    },
  },
};

export const GeospatialData: Story = {
  args: {
    preview: {
      headers: ['property_id', 'address', 'latitude', 'longitude', 'lot_size_sqft', 'zoning_code', 'has_pool'],
      data: [
        ['1001', '123 Main St', '40.7128', '-74.0060', '5000.5', 'R1', 'false'],
        ['1002', '456 Oak Ave', '34.0522', '-118.2437', '7500.0', 'R2', 'true'],
        ['1003', '789 Pine Rd', '41.8781', '-87.6298', '6200.25', 'C1', 'false'],
        ['1004', '321 Elm St', '29.7604', '-95.3698', '4800.75', 'R1', 'false'],
        ['1005', '654 Maple Dr', '39.9526', '-75.1652', '8900.0', 'R3', 'true'],
      ],
    },
    showMappingOptions: true,
    columnMappings: {
      'property_id': 'id',
      'address': 'street_address',
      'latitude': 'lat',
      'longitude': 'lng',
      'lot_size_sqft': 'lot_area',
      'zoning_code': 'zone',
      'has_pool': 'pool_indicator',
    },
  },
};

export const FinancialData: Story = {
  args: {
    preview: {
      headers: ['transaction_id', 'account_number', 'amount', 'currency', 'transaction_date', 'is_verified', 'transaction_type'],
      data: [
        ['10001', 'ACC-001', '1250.50', 'USD', '2023-12-01', 'true', 'debit'],
        ['10002', 'ACC-002', '2500.00', 'EUR', '2023-12-02', 'true', 'credit'],
        ['10003', 'ACC-003', '750.25', 'GBP', '2023-12-03', 'false', 'debit'],
        ['10004', 'ACC-004', '3200.75', 'USD', '2023-12-04', 'true', 'credit'],
        ['10005', 'ACC-005', '900.00', 'CAD', '2023-12-05', 'false', 'debit'],
      ],
    },
  },
};

export const LargeDataset: Story = {
  args: {
    preview: {
      headers: ['id', 'name', 'email', 'city', 'state', 'zip', 'country', 'signup_date', 'last_login'],
      data: Array.from({ length: 50 }, (_, i) => [
        `${1000 + i}`,
        `User ${i + 1}`,
        `user${i + 1}@example.com`,
        `City${i % 10}`,
        `State${i % 5}`,
        `${10000 + i}`,
        i % 3 === 0 ? 'USA' : i % 3 === 1 ? 'Canada' : 'Mexico',
        `2023-${String(Math.floor(i / 4) % 12 + 1).padStart(2, '0')}-${String(i % 28 + 1).padStart(2, '0')}`,
        `2023-${String(Math.floor(i / 3) % 12 + 1).padStart(2, '0')}-${String(i % 28 + 1).padStart(2, '0')}`,
      ]),
    },
  },
};

export const EmptyData: Story = {
  args: {
    preview: {
      headers: [],
      data: [],
    },
  },
};

export const SingleRow: Story = {
  args: {
    preview: {
      headers: ['header1', 'header2', 'header3'],
      data: [
        ['value1', 'value2', 'value3'],
      ],
    },
  },
};
