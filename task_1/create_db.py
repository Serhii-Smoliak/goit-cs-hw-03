import psycopg2
from psycopg2 import sql, extensions

db_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**db_params)
    conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()

    cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), (db_params["dbname"],))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_params["dbname"])))

    cur.close()
    conn.close()

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    tables = ['users', 'status', 'tasks']
    for table in tables:
        cur.execute(f"SELECT to_regclass('{table}')")
        exists = cur.fetchone()[0]
        if not exists:
            if table == 'users':
                cur.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        fullname VARCHAR(100),
                        email VARCHAR(100) UNIQUE
                    )
                """)
            elif table == 'status':
                cur.execute("""
                    CREATE TABLE status (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) UNIQUE
                    )
                """)
                cur.execute("""
                    INSERT INTO status (name) VALUES ('new'), ('in progress'), ('completed')
                """)
            elif table == 'tasks':
                cur.execute("""
                    CREATE TABLE tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(100),
                        description TEXT,
                        status_id INTEGER REFERENCES status(id),
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
                    )
                """)

    conn.commit()
    cur.close()
    conn.close()

    print("All tables have been successfully created.")

except psycopg2.Error as e:
    print(f"An error occurred while connecting to the database: {e}")
