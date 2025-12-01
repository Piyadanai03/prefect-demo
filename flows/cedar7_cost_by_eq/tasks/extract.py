from __future__ import annotations

import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text

from flows.db import get_sqlserver_engine
from flows.observability import get_tracer

tracer = get_tracer(__name__)

_COST_BY_EQ_SOURCE_QUERY = """
SELECT
    e.EQNO,
    e.EQName,
    e.EQCode,
    wo.WODATE,
    wo.SiteNo,
    wt.WOTypeGroupNo,
    COUNT(wo.WONO) AS wo_count,
    SUM(CASE WHEN wr.RESCTYPE = 'L' THEN wr.amount ELSE 0 END) AS MHCost,
    SUM(CASE WHEN wr.RESCTYPE = 'P' AND wr.RESCSUBTYPE IN ('N','S') THEN wr.amount ELSE 0 END) AS SparePartCost,
    SUM(CASE WHEN wr.RESCTYPE = 'O' AND wr.RESCSUBTYPE IN ('O','V') THEN wr.amount ELSE 0 END) AS OutsourceCost,
    SUM(
        CASE
            WHEN wr.RESCTYPE = 'L' THEN wr.amount
            WHEN wr.RESCTYPE = 'P' AND wr.RESCSUBTYPE IN ('N','S') THEN wr.amount
            WHEN wr.RESCTYPE = 'O' AND wr.RESCSUBTYPE IN ('O','V') THEN wr.amount
            ELSE 0
        END
    ) AS maincost
FROM WO AS wo
LEFT JOIN WO_Resource AS wr ON wr.WONO = wo.WONO
LEFT JOIN EQ AS e ON e.EQNO = wo.EQNO
LEFT JOIN WOTYPE AS wt ON wt.WOTYPENO = wo.WOTYPENO
WHERE e.EQNO IS NOT NULL
GROUP BY e.EQNO, e.EQName, e.EQCode, wo.WODATE, wo.SiteNo, wt.WOTypeGroupNo
"""


@task(name="cedar7-extract-cost-by-eq")
def extract_cost_by_eq_data() -> pd.DataFrame:
    """Read source data from SQL Server with tracing."""
    logger = get_run_logger()
    
    with tracer.start_as_current_span("extract-sql-server") as span:
        logger.info("Connecting to SQL Server …")
        span.set_attribute("db.system", "mssql")
        span.set_attribute("db.operation", "SELECT")
        
        engine = get_sqlserver_engine()
        
        with tracer.start_as_current_span("execute-query"):
            with engine.connect() as conn:
                df = pd.read_sql(text(_COST_BY_EQ_SOURCE_QUERY), conn)
        
        span.set_attribute("db.rows_returned", len(df))
        logger.info("Extracted %s rows", len(df))
        
    return df