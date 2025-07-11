# NNDR Insight Developer Overview

## 1. API Endpoints

### Ingestion
- **POST `/api/ingestions/upload`**
  - Upload a file for ingestion to a specified staging table.
  - **Request:**
    - `file`: File (form-data)
    - `table_name`: string (form-data, must be a valid staging table)
  - **Response:**
    - `{ filename, table_name, message }`
  - **Notes:** File is saved to `/tmp/`. Ingestion logic can be extended.

### Master Data
- **GET `/api/admin/master/tables`**
  - Returns the list of master tables and their relationships (edges).
  - **Response:**
    - `{ master_tables: [string], table_edges: [{source, target, label}] }`

- **GET `/api/admin/master/preview/{table_name}`**
  - Paginated preview of master table data.
  - **Query params:** `page_size`, `offset`
  - **Response:** `{ table_name, total_count, sample_data }`

### Staging Data
- **GET `/api/admin/staging/preview/{table_name}`**
  - Paginated preview of staging table data with filter options.
  - **Query params:** `batch_id`, `source_name`, `session_id`, `page_size`, `offset`
  - **Response:** `{ table_name, total_count, sample_data, filter_options, applied_filters }`

- **POST `/api/admin/staging/migrate/{table_name}`**
  - Migrate data from staging to master table, mapping only relevant columns.
  - **Body:** `{ batch_id?, source_name?, session_id? }`
  - **Response:** Migration summary.

### Auth & RBAC
- **POST `/api/admin/user/login`**: Obtain JWT token.
- **GET `/api/admin/user/me`**: Get current user info (for session restore).
- **GET `/api/admin/users`**: List users (admin/power_user only).

## 2. Frontend Usage Notes
- **Master Data Page**: Fetches master tables/relationships from `/api/admin/master/tables`. Paginated preview and row selection use `/api/admin/master/preview/{table_name}`.
- **Staged Data Page**: Uses `/api/admin/staging/preview/{table_name}` for preview and filters. Migration uses `/api/admin/staging/migrate/{table_name}`.
- **File Upload**: Uses `/api/ingestions/upload` for uploading files to staging tables.
- **RBAC**: Sidebar/topbar and routes are rendered based on user role. All routes except `/login` require authentication.

## 3. Migration & Indexing Guidance
- **Migration Logic**: Only columns present in both staging and master tables (excluding metadata like `batch_id`, `source_name`, etc.) are migrated. Types are cast as needed.
- **Indexing**: For large staging tables, add indexes on metadata columns (`batch_id`, `source_name`, `session_id`) to improve filter/query performance.
- **DDL Location**: Keep DDL statements in `.sql` files, not embedded in Python scripts.

## 4. Accessibility & UI/UX Improvements
- **Master Data Page**: 
  - All interactive elements have ARIA labels and roles.
  - Keyboard navigation for table rows and diagram nodes.
  - Improved color contrast and focus indicators.
  - Skip-to-content link for screen readers.
- **General**: Consistent styling, clear loading/error states, tooltips, and helper text.

## 5. How to Extend
- **Ingestion**: Extend `/api/ingestions/upload` to trigger actual ingestion logic after file save.
- **New Tables**: Add new master/staging tables in the database and update `/api/admin/master/tables` as needed.
- **RBAC**: Add new roles or permissions in the backend and update frontend menu logic.
- **Testing**: Add backend and frontend tests for new features/endpoints.

---

For further details, see the code in `backend/app/routers/`, `frontend/src/pages/`, and the SQL schema files in `db_setup/schemas/`. 