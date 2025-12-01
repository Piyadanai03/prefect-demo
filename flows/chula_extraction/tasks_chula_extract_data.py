from prefect import task, get_run_logger
import pandas as pd
from pathlib import Path
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from flows.db import get_sqlserver_engine


@task(name="chula-extract-table")
def extract_table_data(table_name: str, limit: int = 1000) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Connecting to SQL Server...")

    engine = get_sqlserver_engine()
    logger.info("✓ Connected successfully")
    logger.info(f"Extracting data from table: {table_name}")


    if '.' in table_name:
        parts = table_name.split('.')
        quoted_table = f"[{parts[0]}].[{parts[1]}]"
    else:
        quoted_table = f"[dbo].[{table_name}]"

    query = f"SELECT TOP {limit} * FROM {quoted_table}"
    logger.info(f"Executing query: {query}")

    df = pd.read_sql(query, engine)

    logger.info(f"✓ Extracted {len(df)} rows, {len(df.columns)} columns")

    return df


@task(name="chula-save-csv")
def save_to_csv(df: pd.DataFrame, output_path: str) -> str:
    logger = get_run_logger()
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine output format based on file extension
    if output_path.endswith('.json'):
        df.to_json(output_path, orient='records', indent=2, date_format='iso')
        logger.info(f"✓ Saved to {output_path} (JSON format)")
    else:
        df.to_csv(output_path, index=False)
        logger.info(f"✓ Saved to {output_path} (CSV format)")
    
    logger.info(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
    
    return output_path


