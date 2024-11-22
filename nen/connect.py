import psycopg2

# Function to connect to the PostgreSQL database
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="AnhVienTham",
            user="postgres",
            password="khongnho",
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
