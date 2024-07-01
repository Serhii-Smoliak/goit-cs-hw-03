import psycopg2
from faker import Faker

fake = Faker()

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="root",
        host="localhost",
        port="5432"
    )

    cur = conn.cursor()

    for _ in range(15):
        fullname = fake.name()
        email = fake.name().replace(' ', '.').lower() + '@' + fake.domain_name()
        cur.execute("INSERT INTO users (fullname, email) VALUES (%s, %s)", (fullname, email))

    cur.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cur.fetchall()]

    for user_id in user_ids[:10]:
        for i in range(10):
            title = fake.sentence()
            description = fake.text() if i < 7 else None
            status_id = fake.random_int(min=1, max=3)
            cur.execute("INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s)",
                        (title, description, status_id, user_id))

    conn.commit()

    cur.close()
    conn.close()

    print("All seeds have been successfully inserted.")

except psycopg2.Error as e:
    print(f"An error occurred while connecting to the database or executing SQL queries: {e}")
