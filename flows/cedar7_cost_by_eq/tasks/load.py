from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text, inspect

from flows.db import get_postgres_engine_localhost


@task(name="cedar7-load-cost-by-eq")
def load_cost_by_eq_data(
    df: pd.DataFrame,
    destination_table: str = "cost_by_eq",
    destination_schema: Optional[str] = None,
    truncate_before_load: bool = False,
    chunksize: int = 1000,
) -> Dict[str, Any]:
    """Write transformed data into the cedar_dashboard PostgreSQL database."""
    logger = get_run_logger()
    qualified_table = (
        f"{destination_schema}.{destination_table}"
        if destination_schema
        else destination_table
    )

    if df.empty:
        logger.warning("No rows to load into %s; skipping load step", destination_table)
        return {
            "rows_inserted": 0,
            "table": destination_table,
            "schema": destination_schema,
            "qualified_table": qualified_table,
        }

    engine = get_postgres_engine_localhost()

    with engine.begin() as conn:
        if truncate_before_load:
            inspector = inspect(conn)
            table_exists = inspector.has_table(destination_table, schema=destination_schema)
            
            if table_exists:
                logger.info("Truncating %s", qualified_table)
                conn.execute(text(f"TRUNCATE TABLE {qualified_table}"))
            else:
                logger.info("Table %s does not exist yet. Skipping truncate.", qualified_table)

        df.to_sql(
            destination_table,
            conn,
            schema=destination_schema,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize,
        )

    logger.info("Loaded %s rows into %s", len(df), qualified_table)
    return {
        "rows_inserted": len(df),
        "table": destination_table,
        "schema": destination_schema,
        "qualified_table": qualified_table,
    }