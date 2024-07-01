import re
import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import json_util
from faker import Faker

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

fake = Faker()

try:
    client = MongoClient("mongodb+srv://goitlearn:g6t1TnE2pKRzZJnf@cluster0.02jkjf6.mongodb.net/goit?retryWrites=true&w=majority&appName=Cluster0")
    db = client.goit
    collection = db.cats
except PyMongoError as error:
    print(f"An error occurred while connecting to MongoDB: {error}")


def colored_print_json(data):
    """
    The function prints data in color: keys in red, values in green.
    """
    for record in data:
        json_record = json.dumps(record, default=json_util.default, ensure_ascii=False, indent=4)
        for line in json_record.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                print(f"{RED}{key}:{RESET}{GREEN}{value}{RESET}")
            else:
                print(line)


def color_text(text, color_code):
    """
    A function that takes a text and returns it colored with the provided color code.
    """
    print(f"{color_code}{text}{RESET}")


def add_fake_cat():
    """
    A function that adds a new fake cat document to the collection.
    """
    cat_data = {
        "name": fake.first_name(),
        "age": fake.random_int(min=1, max=20),
        "features": [fake.word(), fake.word(), fake.word()]
    }
    try:
        collection.insert_one(cat_data)
        color_text("Random cat has been added.", GREEN)
    except PyMongoError as error:
        color_text(f"An error occurred while adding the fake cat: {error}", RED)


def get_all_cats():
    """
    A function to output all records from a collection
    """
    cats = list(collection.find({}))
    if not cats:
        return color_text("No records found.", RED)
    colored_print_json(cats)


def get_cat_by_name(name):
    """
    A function that allows the user to enter a cat's name and displays information about that cat
    """
    regex = re.compile(name, re.IGNORECASE)
    cats = list(collection.find({"name": regex}))
    if not cats:
        return color_text(f"No cats found with the name {name}.", RED)
    colored_print_json(cats)


def update_cat_age(name, age):
    """
    A feature that allows the user to update the cat's age by name
    """
    result = collection.update_one({"name": name}, {"$set": {"age": age}})
    if result.modified_count == 0:
        color_text(f"No cats found with the name {name}.", RED)
    else:
        color_text(f"Age has been updated for cat named {name}.", GREEN)


def add_feature_to_cat(name, feature):
    """
    A function that allows you to add a new characteristic to the list of features of a cat by name
    """
    result = collection.update_one({"name": name}, {"$push": {"features": feature}})
    if result.modified_count == 0:
        color_text(f"No cats found with the name {name}.", RED)
    else:
        color_text(f"Feature has been added to cat named {name}.", GREEN)


def delete_cat_by_name(name):
    """
    Function to delete a record from the collection by the name of the animal
    """
    result = collection.delete_one({"name": name})
    if result.deleted_count == 0:
        color_text(f"No cats found with the name {name}.", RED)
    else:
        color_text(f"Cat with the name {name} has been deleted.", GREEN)


def delete_all_cats():
    """
    A function to remove all records from a collection
    """
    try:
        collection.delete_many({})
        color_text("All cats have been deleted.", GREEN)
    except PyMongoError as error:
        color_text(f"An error occurred while deleting all cats: {error}", RED)


def main():
    """
    The entry point of the program, handling user input and executing corresponding database operations.
    """
    while True:
        print("1. Add random cat")
        print("2. Get all cats")
        print("3. Get cat by name")
        print("4. Update cat age")
        print("5. Add feature to cat")
        print("6. Delete cat by name")
        print("7. Delete all cats")

        print("Enter 'q' to quit")

        command = input("Enter command: ")
        if command == 'q':
            break

        try:
            if command == '1':
                add_fake_cat()
            elif command == '2':
                get_all_cats()
            elif command == '3':
                name = input("Enter cat name: ")
                get_cat_by_name(name)
            elif command == '4':
                name = input("Enter cat name: ")
                age = int(input("Enter new age: "))
                update_cat_age(name, age)
            elif command == '5':
                name = input("Enter cat name: ")
                feature = input("Enter new feature: ")
                add_feature_to_cat(name, feature)
            elif command == '6':
                name = input("Enter cat name: ")
                delete_cat_by_name(name)
            elif command == '7':
                delete_all_cats()
        except PyMongoError as error:
            print(f"An error occurred while executing the command {command}: {error}")
        except ValueError as error:
            print(f"An error occurred while parsing the input for command {command}: {error}")
        except Exception as error:
            print(f"An unexpected error occurred while executing the command {command}: {error}")
        while input("Press ENTER to continue...") != '':
            pass


if __name__ == "__main__":
    main()
