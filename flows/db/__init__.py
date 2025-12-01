from sqlalchemy import Engine
from prefect_sqlalchemy import SqlAlchemyConnector

def get_sqlserver_engine(block_name: str = "cedar-sqlserver-creds") -> Engine:
    """Load SQL Server engine from Prefect Block."""
    connector = SqlAlchemyConnector.load(block_name)
    return connector.get_engine()

def get_postgres_engine(block_name: str = "cedar-postgres-creds") -> Engine:
    """Load Postgres engine from Prefect Block."""
    connector = SqlAlchemyConnector.load(block_name)
    return connector.get_engine(pool_pre_ping=True)

def get_postgres_engine_localhost(block_name: str = "postgres-localhost") -> Engine:
    """Load Postgres engine from Prefect Block."""
    connector = SqlAlchemyConnector.load(block_name)
    return connector.get_engine(pool_pre_ping=True)

__all__ = [
    "get_sqlserver_engine",
    "get_postgres_engine",
    "get_postgres_engine_localhost",
]