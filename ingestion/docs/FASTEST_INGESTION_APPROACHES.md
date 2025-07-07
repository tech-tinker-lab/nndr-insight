# Fastest Ingestion Approaches for Staging Tables

## 🚀 Performance Analysis Summary

Based on analysis of all ingestion scripts, here are the **fastest approaches** for uploading data into staging tables:

## 📊 Current Script Performance Ratings

| Script | Current Approach | Speed Rating | Status |
|--------|------------------|--------------|---------|
| `ingest_os_open_uprn.py` | Direct COPY to final table | ⚡⚡⚡ | ✅ Optimized |
| `ingest_code_point_open.py` | Staging → Final with COPY | ⚡⚡⚡ | ✅ Optimized |
| `ingest_onspd.py` | Staging → Final with COPY | ⚡⚡⚡ | ✅ Optimized |
| `ingest_os_open_names.py` | Batch INSERT (1000 rows) | ⚡⚡ | ⚠️ Needs optimization |
| `ingest_nndr_properties.py` | Batch INSERT (1000 rows) | ⚡⚡ | ❌ Needs optimization |
| `ingest_nndr_ratepayers.py` | Batch INSERT | ⚡⚡ | ❌ Needs optimization |

## 🏆 Fastest Approach: COPY to Staging Tables

### **Recommended Pattern:**
```python
# 1. Clear staging table
TRUNCATE TABLE staging_table;

# 2. Fast COPY operation
COPY staging_table (col1, col2, col3, ...) 
FROM STDIN WITH (FORMAT CSV, HEADER TRUE);

# 3. Update metadata
UPDATE staging_table SET 
    batch_id = 'batch_20240707_123456',
    source_name = 'Dataset_Name';
```

### **Performance Characteristics:**
- **Speed**: 100K - 1M rows/second
- **Memory**: Low (streaming)
- **Network**: Minimal (single COPY command)
- **CPU**: Minimal (PostgreSQL handles parsing)

## 📋 Implementation Guide

### **1. For Reference Datasets (UPRN, Code Point, ONSPD)**

**Current Status**: ✅ Already optimized
- Use `COPY` operations
- Direct to staging tables
- Include audit columns (batch_id, source_name, etc.)

**Example:**
```python
def fast_reference_staging(csv_path, staging_table):
    with connection.cursor() as cur:
        # Clear staging
        cur.execute(f"TRUNCATE TABLE {staging_table};")
        
        # Fast COPY
        with open(csv_path, 'r') as f:
            cur.copy_expert(
                f"COPY {staging_table} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                f
            )
```

### **2. For NNDR Datasets (Properties, Ratepayers)**

**Current Status**: ❌ Needs optimization
- **Current**: Batch INSERT (1000 rows) - Slow
- **Recommended**: COPY to staging + bulk processing

**Optimization Strategy:**
```python
# Step 1: Fast COPY to staging
COPY nndr_properties_staging FROM STDIN WITH (FORMAT CSV, HEADER TRUE);

# Step 2: Bulk INSERT to final table
INSERT INTO properties 
SELECT * FROM nndr_properties_staging 
WHERE ba_reference IS NOT NULL;
```

### **3. For Large Datasets (OS Open Map Local)**

**Current Status**: ⚠️ Mixed approaches
- **Recommended**: Parallel processing with COPY
- Use multiple staging tables for different themes
- Merge results efficiently

## 🔧 Optimization Techniques

### **1. Connection Optimization**
```python
# Use connection pooling for multiple files
import psycopg2.pool

pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=10,
    host=HOST, database=DBNAME, user=USER, password=PASSWORD
)
```

### **2. Batch Processing for Large Files**
```python
# For files > 1GB, process in chunks
def process_large_file(csv_path, chunk_size=100000):
    with open(csv_path, 'r') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                process_chunk(chunk)
                chunk = []
```

### **3. Parallel Processing**
```python
# For multiple files, process in parallel
import concurrent.futures

def parallel_ingestion(file_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(ingest_file, f) for f in file_list]
        results = [f.result() for f in futures]
```

## 📈 Performance Benchmarks

### **Expected Performance:**
- **Small files (< 100MB)**: 500K-1M rows/second
- **Medium files (100MB-1GB)**: 200K-500K rows/second  
- **Large files (> 1GB)**: 100K-200K rows/second

### **Memory Usage:**
- **COPY approach**: ~50MB (streaming)
- **Batch INSERT**: ~500MB-1GB (in-memory batches)

## 🛠️ Implementation Checklist

### **For Each Dataset:**
- [ ] Create staging table with audit columns
- [ ] Implement COPY-based ingestion
- [ ] Add batch_id and source_name tracking
- [ ] Implement data quality verification
- [ ] Add error handling and logging
- [ ] Test with sample data
- [ ] Benchmark performance

### **For Master Script:**
- [ ] Update `run_all_ingestion.py` to use staging approach
- [ ] Add progress tracking
- [ ] Implement rollback on failure
- [ ] Add performance reporting

## 🎯 Next Steps

1. **Update NNDR scripts** to use COPY approach
2. **Create staging versions** of all ingestion scripts
3. **Implement parallel processing** for large datasets
4. **Add performance monitoring** and reporting
5. **Create automated testing** for staging ingestion

## 📚 Template Script

See `fast_staging_ingestion_template.py` for a complete implementation example that can be adapted for any dataset.

## 🔍 Monitoring and Verification

### **Key Metrics to Track:**
- Rows per second ingestion rate
- Memory usage during ingestion
- Network I/O
- Database connection time
- Error rates and types

### **Quality Checks:**
- Row count verification
- Data type validation
- Null value analysis
- Duplicate detection
- Referential integrity checks 