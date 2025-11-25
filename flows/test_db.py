from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy import text

def check_connection(name, query):
    print(f"Testing Block: '{name}' ...")
    try:
        block = SqlAlchemyConnector.load(name)
        with block.get_engine().connect() as conn:
            res = conn.execute(text(query)).fetchone()
            print(f"SUCCESS: {str(res[0])[:50]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    print("Starting DB connection test...")
    check_connection("cedar-sqlserver-creds", "SELECT @@VERSION")
    check_connection("cedar-postgres-creds", "SELECT version()")
    check_connection("postgres-localhost", "SELECT version()")
    print("DB connection test finished.")
