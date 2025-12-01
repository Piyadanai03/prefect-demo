from __future__ import annotations

from typing import Dict

from opentelemetry import trace
from prefect import flow, get_run_logger

from .tasks import (
    extract_cost_by_eq_data,
    transform_cost_by_eq_data,
    load_cost_by_eq_data,
)
from flows.observability import setup_telemetry, get_tracer

# ตั้งค่า telemetry
setup_telemetry(service_name="cedar7-cost-by-eq-flow")
tracer = get_tracer(__name__)


@flow(name="cedar7-cost-by-eq", log_prints=True)
def sync_cost_by_eq() -> Dict[str, int]:
    """Run the cedar7 cost_by_eq ETL with tracing."""
    logger = get_run_logger()
    
    with tracer.start_as_current_span("cedar7-cost-by-eq-etl") as span:
        
        trace_id = format(span.get_span_context().trace_id, "032x")
        logger.info(f"🚀 Starting cedar7 cost_by_eq ETL [trace_id={trace_id}]")

        span.set_attribute("flow.name", "cedar7-cost-by-eq")
        
        try:
            # Extract
            with tracer.start_as_current_span("extract-phase"):
                extracted_df = extract_cost_by_eq_data()
                span.set_attribute("rows.extracted", len(extracted_df))
                logger.info("📥 Extracted %s rows", len(extracted_df))
            
            # Transform
            with tracer.start_as_current_span("transform-phase"):
                transformed_df = transform_cost_by_eq_data(extracted_df)
                span.set_attribute("rows.transformed", len(transformed_df))
                logger.info("🔄 Transformed %s rows", len(transformed_df))
            
            # Load
            with tracer.start_as_current_span("load-phase"):
                load_stats = load_cost_by_eq_data(
                    transformed_df,
                    truncate_before_load=True,
                )
                span.set_attribute("rows.loaded", load_stats["rows_inserted"])
                span.set_attribute("destination.table", load_stats["qualified_table"])
                logger.info("📤 Loaded %s rows", load_stats["rows_inserted"])

            run_summary = {
                "rows_extracted": len(extracted_df),
                "rows_loaded": load_stats["rows_inserted"],
                "destination": load_stats["qualified_table"],
            }
            
            logger.info("✅ ETL finished: %s", run_summary)
            return run_summary

        except Exception as e:
            
            logger.error(f"❌ ETL Failed [trace_id={trace_id}]: {e}")
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise e