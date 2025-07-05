# NNDR Data Ingestion Guide

This guide explains how to ingest all NNDR (National Non-Domestic Rates) data into your PostgreSQL/PostGIS database for South Cambridgeshire District Council.

## 🎯 Overview

The data ingestion process will:

1. **Create all database schemas** (master gazetteer, forecasting system)
2. **Ingest geospatial reference data** (postcodes, addresses, boundaries)
3. **Ingest NNDR business rate data** (2023, 2017, 2010)
4. **Create performance indexes**
5. **Run initial analysis queries**

## 📁 Data Sources

The ingestion script expects the following data structure in `backend/data/`:

```
backend/data/
├── codepo_gb/                    # Postcode data (CodePoint Open)
│   └── Data/CSV/
├── opname_csv_gb/                # Address data (OS Open Names)
│   └── Data/
├── opmplc_gml3_gb/               # Property boundaries (OS MasterMap)
├── LAD_MAY_2025_UK_BFC.shp       # Local Authority boundaries
├── uk-englandwales-ndr-2023-*    # NNDR 2023 data
├── uk-englandwales-ndr-2017-*    # NNDR 2017 data
├── uk-englandwales-ndr-2010-*    # NNDR 2010 data
└── Additional NNDR files...
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

Run the automated deployment script from your project root:

**Windows Batch:**
```cmd
run-data-ingestion.bat
```

**PowerShell:**
```powershell
.\run-data-ingestion.ps1
```

This will:
- Transfer all files to your remote server
- Install Python dependencies
- Run the complete ingestion process
- Show database statistics

### Option 2: Manual Deployment

1. **Transfer files to remote server:**
```bash
scp -r setup/database/ user@192.168.1.79:/server/postgis/
scp -r backend/data/ user@192.168.1.79:/server/postgis/
```

2. **Install dependencies:**
```bash
ssh user@192.168.1.79
cd /server/postgis
pip install -r requirements.txt
```

3. **Run ingestion:**
```bash
python3 ingest_all_data.py
```

## 📊 Database Tables Created

### Master Gazetteer Tables
- `postcodes` - UK postcode data with coordinates
- `addresses` - Property addresses from OS Open Names
- `local_authority_boundaries` - LA boundary polygons
- `master_gazetteer` - Consolidated property reference

### NNDR Business Rate Tables
- `nndr_list_entries_2023` - Current business rate list
- `nndr_list_entries_2017` - 2017 business rate list
- `nndr_list_entries_2010` - 2010 business rate list
- `nndr_summary_valuations_2023` - 2023 summary valuations
- `nndr_summary_valuations_2017` - 2017 summary valuations
- `nndr_summary_valuations_2010` - 2010 summary valuations

### Forecasting System Tables
- `forecast_models` - Model configurations
- `forecast_results` - Forecasting outputs
- `forecast_accuracy` - Model performance metrics
- `business_rate_forecasts` - Rate predictions

## ⏱️ Expected Processing Times

| Data Type | Size | Time |
|-----------|------|------|
| Postcodes | ~2.5M records | 5-10 minutes |
| Addresses | ~3M records | 10-15 minutes |
| NNDR 2023 | ~2M records | 15-20 minutes |
| NNDR 2017 | ~1.8M records | 10-15 minutes |
| NNDR 2010 | ~1.5M records | 8-12 minutes |
| **Total** | **~10M records** | **45-75 minutes** |

## 🔧 Configuration

### Database Connection
Edit `ingest_all_data.py` to modify database settings:

```python
self.db_config = {
    'host': '192.168.1.79',
    'port': 5432,
    'database': 'nndr_insight',
    'user': 'nndr_user',
    'password': 'nndr_password'
}
```

### Data Processing Options
- **Chunk size**: Modify `chunk_size = 10000` for memory optimization
- **Address limit**: Change `address_files[:5]` to process more address files
- **Index creation**: Customize indexes in `create_indexes()` method

## 📈 Monitoring Progress

The script provides detailed logging:

```bash
# View real-time progress
tail -f data_ingestion.log

# Check database statistics
docker exec -it $(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c "SELECT schemaname, tablename, n_tup_ins as rows FROM pg_stat_user_tables ORDER BY n_tup_ins DESC;"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Memory Errors**
   - Reduce chunk size in the script
   - Process fewer files at once
   - Increase server memory

2. **Connection Timeouts**
   - Check database is running: `docker ps`
   - Verify network connectivity
   - Increase connection timeout settings

3. **Missing Data Files**
   - Verify all data files are in `backend/data/`
   - Check file permissions
   - Ensure files are not corrupted

4. **Python Package Issues**
   - Install system dependencies: `apt-get install python3-dev libpq-dev`
   - Use virtual environment
   - Update pip: `pip install --upgrade pip`

### Error Recovery

If ingestion fails partway through:

1. **Check logs:**
```bash
cat data_ingestion.log
```

2. **Restart from specific step:**
```python
# Modify ingest_all_data.py to skip completed steps
# Comment out completed sections in run_complete_ingestion()
```

3. **Clean and restart:**
```sql
-- Drop tables and restart
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## 📋 Post-Ingestion Tasks

After successful ingestion:

1. **Verify data quality:**
```sql
SELECT COUNT(*) FROM nndr_list_entries_2023;
SELECT COUNT(DISTINCT ba_reference) FROM nndr_list_entries_2023;
```

2. **Run business rate analysis:**
```sql
-- Properties by rateable value band
SELECT 
    CASE 
        WHEN rateable_value < 12000 THEN 'Small'
        WHEN rateable_value < 51000 THEN 'Medium'
        ELSE 'Large'
    END as band,
    COUNT(*) as count
FROM nndr_list_entries_2023 
GROUP BY band;
```

3. **Generate forecasting models:**
- Use the forecasting system tables
- Run Prophet or other time series models
- Analyze trends and patterns

## 🔒 Security Considerations

- Database passwords are stored in plain text (consider using environment variables)
- Data files contain sensitive business information
- Ensure proper access controls on the database
- Regular backups of ingested data

## 📞 Support

For issues with data ingestion:

1. Check the log file: `data_ingestion.log`
2. Verify database connectivity
3. Ensure all data files are present and uncorrupted
4. Check system resources (memory, disk space)

## 🎉 Success Indicators

You'll know the ingestion is successful when you see:

```
🎉 Data ingestion completed successfully in 2345.67 seconds
📋 Summary:
   ✅ All database schemas created
   ✅ Geospatial data ingested
   ✅ NNDR data ingested
   ✅ Performance indexes created
   ✅ Initial analysis completed
```

And database statistics showing millions of records across all tables. 