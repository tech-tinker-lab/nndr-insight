# Design System Architecture

## Overview

The Design System is a comprehensive solution that decouples file upload from mapping design, providing AI-powered table design management and intelligent file-to-table matching. It includes full auditing and history tracking for all activities.

## Architecture Components

### 1. Backend Design System (`backend/app/routers/design_system.py`)

**Core Features:**
- **Table Design Management**: Create, update, and manage table designs with column definitions
- **Mapping Configuration**: Define file patterns and mapping rules for automatic matching
- **AI-Powered Matching**: Intelligent matching of files to existing designs
- **Audit Logging**: Complete audit trail for all design system activities

**Key Endpoints:**
- `POST /api/design/tables` - Create table design
- `GET /api/design/tables` - List table designs with filtering
- `GET /api/design/tables/{design_id}` - Get specific table design
- `PUT /api/design/tables/{design_id}` - Update table design
- `POST /api/design/configs` - Create mapping configuration
- `GET /api/design/configs` - List mapping configurations
- `POST /api/design/match` - Match file to designs
- `GET /api/design/audit` - Get audit logs

### 2. Database Schema (`db_setup/schemas/design/01_create_design_schema.sql`)

**Tables:**
- `design.table_designs` - Table design definitions
- `design.mapping_configs` - Mapping configurations
- `design.audit_logs` - Audit trail

**Features:**
- UUID primary keys for scalability
- JSONB columns for flexible data storage
- Comprehensive indexing for performance
- Sample data for common table types

### 3. Frontend Design System (`frontend/src/pages/DesignSystem.jsx`)

**Features:**
- **Visual Table Designer**: Create and edit table designs with column definitions
- **Mapping Configuration Manager**: Define file patterns and mapping rules
- **Audit Log Viewer**: View complete activity history
- **Real-time Updates**: Live updates when designs are modified

### 4. Upload Integration (`frontend/src/components/DesignSystemIntegration.jsx`)

**Features:**
- **AI-Powered Matching**: Automatic file-to-design matching
- **Visual Mapping Interface**: Drag-and-drop column mapping
- **Intelligent Suggestions**: AI-generated mapping recommendations
- **Real-time Validation**: Live validation of mappings

## Setup Instructions

### 1. Database Setup

Run the design system schema setup:

```bash
# Windows
cd setup/scripts
setup_design_system.bat

# Linux/Mac
cd setup/scripts
./setup_design_system.sh
```

### 2. Backend Setup

The design system router is automatically included in `backend/app/main.py`. No additional setup required.

### 3. Frontend Setup

The Design System page is automatically added to the navigation. Access it via:
- Navigation: "Design System" in the sidebar
- Direct URL: `/design-system`

## Usage Workflow

### 1. Creating Table Designs

1. Navigate to Design System → Table Designs
2. Click "Create Design"
3. Fill in design details:
   - **Design Name**: Human-readable name
   - **Table Name**: Database table name (with _staging suffix)
   - **Description**: Detailed description
   - **Table Type**: Category (address, property, postcode, etc.)
   - **Category**: Business classification
4. Add columns with:
   - **Name**: Column name
   - **Type**: Data type (text, integer, numeric, boolean, date)
   - **Description**: Column description
   - **Required**: Whether field is required
5. Save the design

### 2. Creating Mapping Configurations

1. Navigate to Design System → Mapping Configurations
2. Click "Create Configuration"
3. Fill in configuration details:
   - **Configuration Name**: Human-readable name
   - **Table Design**: Select target table design
   - **Priority**: Matching priority (higher = more important)
   - **Source Patterns**: File patterns to match (comma-separated)
4. Save the configuration

### 3. File Upload with AI Matching

1. Navigate to Upload page
2. Upload a file
3. The system automatically:
   - Analyzes file headers and content
   - Matches against existing designs
   - Suggests best-fit designs
   - Generates initial column mappings
4. Review and adjust mappings as needed
5. Proceed with upload

## AI-Powered Features

### 1. Intelligent Matching

The system uses multiple algorithms for matching:

- **Pattern Matching**: File name and type patterns
- **Header Similarity**: Column name similarity
- **Content Analysis**: Data type inference
- **Semantic Matching**: Meaning-based matching

### 2. Automatic Mapping Generation

When a design is selected, the system:

- Maps exact column name matches
- Suggests similar column names
- Infers data types from headers
- Generates default column names
- Calculates confidence scores

### 3. Smart Suggestions

The system provides:

- **Design Recommendations**: Best-fit table designs
- **Mapping Suggestions**: Intelligent column mappings
- **Data Type Inference**: Automatic data type detection
- **Validation Warnings**: Potential mapping issues

## Audit and History

### 1. Comprehensive Logging

All activities are logged with:

- **User ID**: Who performed the action
- **Action Type**: CREATE, UPDATE, DELETE, MATCH, VIEW
- **Resource Type**: table_design, mapping_config, file_analysis
- **Resource ID**: Specific resource identifier
- **Details**: JSON context about the action
- **Timestamp**: When the action occurred

### 2. Audit Log Access

View audit logs via:

- Design System → Audit Logs
- Filter by user, action, resource type, date range
- Export capabilities for compliance

## Best Practices

### 1. Table Design

- Use descriptive design names
- Include comprehensive descriptions
- Choose appropriate table types and categories
- Define required fields clearly
- Use consistent naming conventions

### 2. Mapping Configuration

- Use specific file patterns
- Set appropriate priorities
- Test configurations with sample files
- Document mapping rules

### 3. File Upload

- Use descriptive file names
- Include headers in CSV files
- Validate data before upload
- Review AI-generated mappings

## Troubleshooting

### Common Issues

1. **No Design Matches Found**
   - Check file name patterns in configurations
   - Verify column headers are clear
   - Create new designs for unique file types

2. **Poor Mapping Quality**
   - Review and improve mapping configurations
   - Add more specific patterns
   - Manually adjust generated mappings

3. **Performance Issues**
   - Check database indexes
   - Review audit log size
   - Optimize query patterns

### Debug Mode

Enable debug logging by setting:

```python
# In backend/app/routers/design_system.py
logger.setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Visual Mapping Editor**: Drag-and-drop interface for complex mappings
2. **Template Library**: Pre-built designs for common data types
3. **Machine Learning**: Improved matching algorithms
4. **Collaboration**: Multi-user design editing
5. **Version Control**: Design versioning and rollback
6. **API Integration**: External system integration
7. **Advanced Analytics**: Usage analytics and insights

### Integration Points

1. **Data Quality**: Integration with data quality tools
2. **ETL Pipelines**: Automated data processing
3. **Reporting**: Design usage reports
4. **Compliance**: Regulatory compliance features

## Support

For issues or questions:

1. Check the audit logs for error details
2. Review the troubleshooting section
3. Contact the development team
4. Submit bug reports with detailed information

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: NNDR Insight Development Team 