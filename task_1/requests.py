import psycopg2
from prettytable import PrettyTable

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

db_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}


def color_text(text, color_code):
    """
    A function that takes a text and returns it colored with the provided color code.
    """
    print(f"{color_code}{text}{RESET}")


def get_tasks_by_user(user_id):
    """
    Retrieves all tasks assigned to a user by their ID.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                return color_text(f"No user found with ID {user_id}.", RED)

            cur.execute("""
                SELECT * FROM tasks
                WHERE user_id = %s
            """, (user_id,))
            result = cur.fetchall()
            if not result:
                color_text(f"No tasks found for user with ID {user_id}.", RED)
            else:
                return print_table(result, ["Task ID", "Title", "Description", "Status ID", "User ID"])


def get_tasks_by_status(status):
    """
    Retrieves tasks based on their status.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM status WHERE name = %s", (status,))
            status_exists = cur.fetchone()
            if not status_exists:
                return color_text(f"No status found with name {status}.", RED)

            cur.execute("SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name = %s)", (status,))
            result = cur.fetchall()
            if not result:
                color_text(f"No tasks found with status {status}.", RED)
            else:
                return print_table(result, ["Task ID", "Title", "Description", "Status ID", "User ID"])


def update_task_status(task_id, new_status):
    """
    Updates the status of a specific task.
    """
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM status WHERE name = %s", (new_status,))
                status_exists = cur.fetchone()
                if not status_exists:
                    return color_text(f"No status found with name {new_status}.", RED)

                cur.execute("UPDATE tasks SET status_id = %s WHERE id = %s", (status_exists[0], task_id))
                if cur.rowcount == 0:
                    return color_text(f"No task found with ID {task_id}.", RED)

                conn.commit()
                color_text("Task status has been updated.", GREEN)
    except psycopg2.Error as error:
        color_text(f"An error occurred while updating the task status: {error}", RED)


def get_users_without_tasks():
    """
    Retrieves all users who have no tasks assigned to them.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks)")
            result = cur.fetchall()
            if not result:
                color_text("All users have tasks assigned to them.", GREEN)
            else:
                print_table(result, ["User ID", "Full Name", "Email"])


def add_task_for_user(user_id, title, description, status_id):
    """
     Adds a new task for a specific user.
    """
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if not user:
                    return color_text(f"No user found with ID {user_id}.", RED)

                cur.execute("INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s)",
                            (title, description, status_id, user_id))
                conn.commit()
                color_text("Task has been added.", GREEN)
    except psycopg2.Error as error:
        color_text(f"An error occurred while adding the task: {error}", RED)


def get_uncompleted_tasks():
    """
    Retrieves all tasks that are not completed.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name = 'completed')")
            result = cur.fetchall()
            if not result:
                color_text("All tasks are completed.", GREEN)
            else:
                print_table(result, ["Task ID", "Title", "Description", "Status ID", "User ID"])


def delete_task(task_id):
    """
    Deletes a specific task.
    """
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                if cur.rowcount == 0:
                    return color_text(f"No task found with ID {task_id}.", RED)
                conn.commit()
                color_text("Task has been deleted.", GREEN)
    except psycopg2.Error as error:
        color_text(f"An error occurred while deleting the task: {error}", RED)


def find_users_by_email(email):
    """
    Finds users by their email address.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email LIKE %s", ('%' + email + '%',))
            result = cur.fetchall()
            if not result:
                color_text(f"No users found with email {email}.", RED)
            else:
                print_table(result, ["User ID", "Full Name", "Email"])


def update_user_name(user_id, new_name):
    """
    Updates the name of a specific user.
    """
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if not user:
                    return color_text(f"No user found with ID {user_id}.", RED)

                cur.execute("UPDATE users SET fullname = %s WHERE id = %s", (new_name, user_id))
                if cur.rowcount == 0:
                    return color_text(f"No user found with ID {user_id}.", RED)
                conn.commit()
                color_text("User name has been updated.", GREEN)
    except psycopg2.Error as e:
        color_text(f"An error occurred while updating the user name: {e}", RED)


def get_task_count_by_status():
    """
    Retrieves the count of tasks grouped by their status.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status_id, COUNT(*) FROM tasks GROUP BY status_id")
            result = cur.fetchall()
            if not result:
                color_text("No tasks found.", RED)
            else:
                print_table(result, ["Status ID", "Task Count"])


def get_tasks_by_email_domain(domain):
    """
    Retrieves tasks assigned to users with a specific email domain.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tasks.* FROM tasks
                JOIN users ON tasks.user_id = users.id
                WHERE users.email LIKE %s
            """, ('%@' + domain,))
            result = cur.fetchall()
            if not result:
                color_text(f"No tasks found for users with email domain {domain}.", RED)
            else:
                print_table(result, ["Task ID", "Title", "Description", "Status ID", "User ID"])


def get_tasks_without_description():
    """
    Retrieves all tasks that do not have a description.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE description IS NULL OR description = ''")
            result = cur.fetchall()
            if not result:
                color_text("No tasks found without description.", GREEN)
            else:
                print_table(result, ["Task ID", "Title", "Description", "Status ID", "User ID"])


def get_in_progress_tasks():
    """
    Retrieves all tasks that are currently in progress.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT users.id, users.fullname, users.email, tasks.id, tasks.title, tasks.description, tasks.status_id
                FROM users
                INNER JOIN tasks ON users.id = tasks.user_id
                WHERE tasks.status_id = (SELECT id FROM status WHERE name = 'in progress')
            """)
            result = cur.fetchall()
            if not result:
                color_text("No tasks are in progress.", GREEN)
            else:
                print_table(result, ["User ID", "Full Name", "Email", "Task ID", "Title", "Description", "Status ID"])


def get_users_and_task_count():
    """
    Retrieves all users along with the count of tasks assigned to them.
    """
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT users.*, COUNT(tasks.id) FROM users
                LEFT JOIN tasks ON users.id = tasks.user_id
                GROUP BY users.id ORDER BY users.id
            """)
            result = cur.fetchall()
            if not result:
                color_text("No users found.", RED)
            else:
                print_table(result, ["User ID", "Full Name", "Email", "Task Count"])


def print_table(data, columns):
    """
    Prints data in a table format.
    """
    table = PrettyTable(columns)
    for row in data:
        table.add_row(row)
    print(table)


def main():
    """
    The entry point of the program, handling user input and executing corresponding database operations.
    """
    while True:
        try:
            print("1. Get tasks by user ID")
            print("2. Get tasks by status")
            print("3. Update task status")
            print("4. Get users without tasks")
            print("5. Add task for user")
            print("6. Get uncompleted tasks")
            print("7. Delete task")
            print("8. Find users by email")
            print("9. Update user name")
            print("10. Get task count by status")
            print("11. Get tasks by email domain")
            print("12. Get tasks without description")
            print("13. Get in progress tasks")
            print("14. Get users and task count")
            print("Enter 'q' to quit")

            command = input("Enter command: ")
            if command == 'q':
                break

            if command == '1':
                user_id = input("Enter user ID: ")
                get_tasks_by_user(user_id)
            elif command == '2':
                status = input("Enter status (new, im progress, completed): ")
                get_tasks_by_status(status)
            elif command == '3':
                task_id = input("Enter task ID: ")
                new_status = input("Enter new status (new, im progress, completed): ")
                update_task_status(task_id, new_status)
            elif command == '4':
                get_users_without_tasks()
            elif command == '5':
                user_id = input("Enter user ID: ")
                title = input("Enter task title: ")
                description = input("Enter task description: ")
                status_id = input("Enter status ID: ")
                add_task_for_user(user_id, title, description, status_id)
            elif command == '6':
                get_uncompleted_tasks()
            elif command == '7':
                task_id = input("Enter task ID: ")
                delete_task(task_id)
            elif command == '8':
                email = input("Enter email: ")
                find_users_by_email(email)
            elif command == '9':
                user_id = input("Enter user ID: ")
                new_name = input("Enter new name: ")
                update_user_name(user_id, new_name)
            elif command == '10':
                get_task_count_by_status()
            if command == '11':
                domain = input("Enter email domain: ")
                get_tasks_by_email_domain(domain)
            elif command == '12':
                get_tasks_without_description()
            elif command == '13':
                get_in_progress_tasks()
            elif command == '14':
                get_users_and_task_count()

        except psycopg2.Error as error:
            color_text(f"An error occurred while executing the command: {error}", RED)
        except Exception as error:
            color_text(f"An unexpected error occurred: {error}", RED)
        while input("Press ENTER to continue...") != '':
            pass


if __name__ == "__main__":
    main()
