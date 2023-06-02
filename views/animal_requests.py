import sqlite3
from models import Animal, Location, Customer

ANIMALS = [
    {
        "id": 1,
        "name": "Snickers",
        "species": "Dog",
        "locationId": 1,
        "customerId": 1,
        "status": "Admitted"
    },
    {
        "id": 2,
        "name": "Roman",
        "species": "Dog",
        "locationId": 1,
        "customerId": 1,
        "status": "Admitted"
    },
    {
        "id": 3,
        "name": "Blue",
        "species": "Cat",
        "locationId": 2,
        "customerId": 1,
        "status": "Admitted"
    }
]

def get_all_animals(query_params):
    """Using SQL database to get all animals"""
    # Open a connection to the database
    with sqlite3.connect("./kennel.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        sort_by = ""
        where_clause = ""

        sort_options = {
            "location": "location_id",
            "customer": "customer_id",
            "status": "status",
            "name": "animal_name"
        }

    # if len(query_params) != 0:
    #     param = query_params[0]
    #     [qs_key, qs_value] = param.split('=')
        for param in query_params:
            qs_key, qs_value = param.split('=')

            if qs_key == "_sortBy" and qs_value in sort_options:
                sort_by = f" ORDER BY {sort_options[qs_value]}"
            elif qs_key == "location_id":
                where_clause = f"WHERE a.location_id = {qs_value}"
            elif qs_key == "status":
                where_clause = f"WHERE a.status = '{qs_value}'"

        sql_to_execute = f""" SELECT
            a.id,
            a.name animal_name,
            a.breed,
            a.customer_id,
            a.location_id,
            a.status,
            l.name location_name,
            l.address location_address,
            c.name customer_name,
            c.address customer_address,
            c.email customer_email,
            c.password customer_password
        FROM Animal a
        JOIN Location l
            ON l.id = a.location_id
        JOIN Customer c
            ON c.id = a.customer_id
        {where_clause}
        {sort_by}
        """
    db_cursor.execute(sql_to_execute)

        # Initialize an empty list to hold all animal representations
    animals = []

        # Convert rows of data into a Python list
    dataset = db_cursor.fetchall()

    for row in dataset:

        # Create an animal instance from the current row
        animal = Animal(row['id'], row['animal_name'],
        row['breed'], row['customer_id'],row['location_id'], row['status'], )

        # Create a Location instance from the current row
        location = Location(row['location_id'], row['location_name'], row['location_address'])

        customer = Customer(row['customer_id'], row['customer_name'],
        row['customer_address'], row['customer_email'], row['customer_password'] )

        # Add the dictionary representation of the location to the animal

        animal.location = location.__dict__
        animal.customer = customer.__dict__

        # Add the dictionary representation of the animal to the list
        animals.append(animal.__dict__)

    return animals


def get_single_animal(id):
    """New single animal request for SQL"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            a.id,
            a.name,
            a.breed,
            a.status,
            a.location_id,
            a.customer_id
        FROM animal a
        WHERE a.id = ?
        """, ( id, ))

        # Load the single result into memory
        data = db_cursor.fetchone()

        # Create an animal instance from the current row
        animal = Animal(data['id'], data['name'], data['breed'],
                            data['status'], data['location_id'],
                            data['customer_id'])

        return animal.__dict__

def get_animals_by_location(location_id):
    """To query animals by location Id in link"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        select
            c.id,
            c.name,
            c.breed,
            c.status,
            c.location_id,
            c.customer_id
        from Animal c
        WHERE c.location_id = ?
        """, ( location_id, ))

        animals = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            animal = Animal(row['id'], row['name'], row['breed'],
            row['status'] , row['location_id'], row['customer_id'])
            animals.append(animal.__dict__)

    return animals

def get_animal_by_status(status):
    """To query a customer by email in link"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        select
            c.id,
            c.name,
            c.breed,
            c.location_id,
            c.customer_id,
            c.status
        from Animal c
        WHERE c.status = ?
        """, ( status, ))

        animals = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            animal = Animal(row['id'], row['name'], row['breed'],
            row['status'] , row['location_id'], row['customer_id'])
            animals.append(animal.__dict__)

    return animals

# Function with a single parameter
# def get_single_animal_old(id):
#     """Sends single animal."""
#     # Variable to hold the found animal, if it exists
#     requested_animal = None

#     # Iterate the ANIMALS list above. Very similar to the
#     # for..of loops you used in JavaScript.
#     for animal in ANIMALS:
#         # Dictionaries in Python use [] notation to find a key
#         # instead of the dot notation that JavaScript used.
#         if animal["id"] == id:
#             requested_animal = animal
#             matching_location = get_single_location(requested_animal["locationId"])
#             requested_animal.pop("locationId")
#             requested_animal["location"] = matching_location
#             matching_customer = get_single_customer(requested_animal["customerId"])
#             requested_animal["customer"] = matching_customer
#             requested_animal.pop("customerId")

#     return requested_animal

def create_animal(new_animal):
    """Add to SQL Database"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Animal
            ( name, breed, status, location_id, customer_id )
        VALUES
            ( ?, ?, ?, ?, ?);
        """, (new_animal['name'], new_animal['breed'],
            new_animal['status'], new_animal['location_id'],
            new_animal['customer_id'], ))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the animal dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_animal['id'] = id


    return new_animal

# def create_animal(animal):
#     """Create New Animal"""
#     # Get the id value of the last animal in the list
#     max_id = ANIMALS[-1]["id"]

#     # Add 1 to whatever that number is
#     new_id = max_id + 1

#     # Add an `id` property to the animal dictionary
#     animal["id"] = new_id

#     # Add the animal dictionary to the list
#     ANIMALS.append(animal)

#     # Return the dictionary with `id` property added
#     return animal

def delete_animal(id):
    """DELETE from SQL database"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM animal
        WHERE id = ?
        """, (id, ))


# def delete_animal(id):
#     """To Delete Animal."""
#     # Initial -1 value for animal index, in case one isn't found
#     animal_index = -1

#     # Iterate the ANIMALS list, but use enumerate() so that you
#     # can access the index value of each item
#     for index, animal in enumerate(ANIMALS):
#         if animal["id"] == id:
#             # Found the animal. Store the current index.
#             animal_index = index

#     # If the animal was found, use pop(int) to remove it from list
#     if animal_index >= 0:
#         ANIMALS.pop(animal_index)

def update_animal(id, new_animal):
    """UPDATE in SQL"""
    with sqlite3.connect("./kennel.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Animal
            SET
                name = ?,
                breed = ?,
                status = ?,
                location_id = ?,
                customer_id = ?
        WHERE id = ?
        """, (new_animal['name'], new_animal['breed'],
            new_animal['status'], new_animal['locationId'],
            new_animal['customerId'], id, ))

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True

# def update_animal(id, new_animal):
#     "Edit Animal."
#     # Iterate the ANIMALS list, but use enumerate() so that
#     # you can access the index value of each item.
#     for index, animal in enumerate(ANIMALS):
#         if animal["id"] == id:
#             # Found the animal. Update the value.
#             ANIMALS[index] = new_animal
#             break
