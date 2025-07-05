import pandas as pd
from pathlib import Path

def load_csv_flexibly(filepath, max_rows=None, delimiter=None, header=None):
    """
    Loads a CSV or delimited file using pandas, supports custom delimiter and chunked reading.
    Returns a list of dicts (records).
    """
    filepath = Path(filepath)
    # Try to auto-detect delimiter if not provided
    if delimiter is None:
        # Read a small sample to guess delimiter
        with open(filepath, encoding='utf-8') as f:
            sample = f.read(2048)
        if '*' in sample and sample.count('*') > sample.count(','):
            delimiter = '*'
        else:
            delimiter = ','
    # Handle header: None for no header, 0 for first row as header
    pandas_header = 0 if (header is None or header != 'none') else None
    # Read in chunks if max_rows is set
    if max_rows:
        df_iter = pd.read_csv(filepath, delimiter=delimiter, header=pandas_header, chunksize=max_rows, encoding='utf-8')
        df = next(df_iter)
    else:
        df = pd.read_csv(filepath, delimiter=delimiter, header=pandas_header, encoding='utf-8')
    # If no header, generate generic column names
    if pandas_header is None:
        df.columns = [f"col{i+1}" for i in range(len(df.columns))]
    return df.to_dict(orient='records')