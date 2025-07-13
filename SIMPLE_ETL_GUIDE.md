# 📊 **Simple ETL Guide - Making Data Transformation Easy**

## 🎯 **What is ETL?**

**ETL** stands for **Extract, Transform, Load**. It's a simple 3-step process:

1. **Extract** - Get your data from files (CSV, Excel, etc.)
2. **Transform** - Clean and format your data
3. **Load** - Put your data into the database

Think of it like moving house:
- **Extract** = Pack your boxes (get data from files)
- **Transform** = Clean and organize your stuff (clean and format data)
- **Load** = Unpack into your new house (put data in database)

---

## 🚀 **How to Use the Simple ETL System**

### **Step 1: Upload Your Data**
- Click "Choose File" and select your CSV, Excel, or JSON file
- The system will show you a preview of your data
- You can see what columns you have and sample data

### **Step 2: Map Your Columns**
- Choose which database table you want to put your data into
- Map your file columns to database columns
- Skip any columns you don't need

### **Step 3: Transform Your Data (Optional)**
- Clean up your data with simple transformations:
  - **Uppercase/Lowercase** - Fix text formatting
  - **Trim** - Remove extra spaces
  - **Number Format** - Clean up currency and numbers
  - **Date Format** - Fix date formats
  - **Postcode Clean** - Standardize UK postcodes
  - **Coordinate Validate** - Check coordinates are valid

### **Step 4: Load Your Data**
- Review your configuration
- Click "Run ETL Process"
- Watch the progress and see results

---

## 📋 **Common Use Cases**

### **Loading Property Data**
1. **Upload** your property CSV file
2. **Map** columns like:
   - `BA_Reference` → `ba_reference`
   - `Postcode` → `postcode`
   - `Rateable_Value` → `rateable_value`
3. **Transform** with:
   - Postcode cleaning
   - Number formatting for values
4. **Load** into the `properties` table

### **Loading Postcode Data**
1. **Upload** your postcode CSV file
2. **Map** columns like:
   - `PCDS` → `pcds`
   - `LAT` → `latitude`
   - `LONG` → `longitude`
3. **Transform** with:
   - Coordinate validation
   - Postcode cleaning
4. **Load** into the `onspd` table

---

## 🔧 **Available Transformations**

| Transformation | What it does | Example |
|----------------|--------------|---------|
| **Uppercase** | Converts text to UPPERCASE | `london` → `LONDON` |
| **Lowercase** | Converts text to lowercase | `LONDON` → `london` |
| **Trim** | Removes extra spaces | `"  London  "` → `"London"` |
| **Number Format** | Cleans numbers and currency | `£1,234.56` → `1234.56` |
| **Date Format** | Fixes date formats | `15/01/2024` → `2024-01-15` |
| **Postcode Clean** | Standardizes UK postcodes | `sw1a 1aa` → `SW1A 1AA` |
| **Coordinate Validate** | Checks coordinates are valid | Validates UK lat/long ranges |

---

## 📊 **Data Validation**

The system automatically checks your data for:
- ✅ **Missing values** - Shows how many empty cells
- ✅ **Data types** - Checks if numbers are really numbers
- ✅ **Postcode format** - Validates UK postcode structure
- ✅ **Coordinate ranges** - Checks if coordinates are in UK
- ✅ **Value ranges** - Flags unusual rateable values

---

## 🎯 **Tips for Success**

### **Before You Start**
1. **Check your file format** - CSV, Excel, JSON, or XML
2. **Look at your data** - Preview shows you what you're working with
3. **Plan your mapping** - Know which columns go where

### **During Mapping**
1. **Start simple** - Map the most important columns first
2. **Use transformations** - Clean up messy data
3. **Skip unnecessary columns** - Don't map columns you don't need

### **Before Loading**
1. **Review the summary** - Check your configuration
2. **Look at warnings** - Fix any issues the system found
3. **Test with small data** - Try with a few rows first

---

## 🚨 **Common Issues & Solutions**

### **"Target table doesn't exist"**
- **Solution**: Make sure the table exists in your database
- **Check**: Use the table list to see available tables

### **"Column mapping error"**
- **Solution**: Check that target columns exist in the table
- **Check**: Use the column list to see available columns

### **"Invalid postcode format"**
- **Solution**: Use the "Postcode Clean" transformation
- **Example**: `sw1a1aa` → `SW1A 1AA`

### **"Coordinate validation failed"**
- **Solution**: Use the "Coordinate Validate" transformation
- **Check**: Make sure coordinates are in UK ranges

---

## 📈 **Monitoring Your ETL Jobs**

After running an ETL job, you can:
- ✅ **See results** - How many records processed
- ✅ **Check errors** - Any problems that occurred
- ✅ **View warnings** - Data quality issues found
- ✅ **Track performance** - How long the job took

---

## 🔍 **Example: Loading Property Data**

Here's a complete example of loading property data:

### **1. Your CSV File**
```csv
BA_Reference,Property_Address,Postcode,Rateable_Value
123456,123 High Street,sw1a 1aa,50000
789012,456 Main Road,ec1a 1bb,75000
```

### **2. Column Mapping**
- `BA_Reference` → `ba_reference`
- `Property_Address` → `property_address`
- `Postcode` → `postcode`
- `Rateable_Value` → `rateable_value`

### **3. Transformations**
- **Postcode**: Apply "Postcode Clean"
- **Rateable_Value**: Apply "Number Format"

### **4. Results**
- ✅ **2 records processed**
- ✅ **2 records loaded**
- ✅ **0 errors**
- ✅ **Processing time: 1.2 seconds**

---

## 🎉 **You're Ready!**

The Simple ETL system makes data loading easy and visual. You can:
- ✅ **Upload any file** - CSV, Excel, JSON, XML
- ✅ **Map columns easily** - Drag and drop interface
- ✅ **Transform data** - Built-in cleaning tools
- ✅ **Validate automatically** - Quality checks
- ✅ **Monitor progress** - Real-time feedback

**Start with a small file to test, then load your full dataset!** 