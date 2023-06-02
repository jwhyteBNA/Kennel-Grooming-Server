import json
from urllib.parse import urlparse
# from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import get_all_animals, get_all_locations, get_all_employees, get_all_customers
from views import get_single_animal, get_single_location, get_single_employee, get_single_customer
from views import create_animal, create_location, create_employee, create_customer
from views import delete_animal, delete_location, delete_employee
from views import update_animal, update_location, update_employee, update_customer
from views import get_customer_by_email, get_employees_by_location
from views import get_animal_by_status, get_animals_by_location

method_mapper = {
    "animals": {
        "single": get_single_animal,
        "all": get_all_animals
    },
    "locations": {
        "single": get_single_location,
        "all": get_all_locations
    },
    "employees": {
        "single": get_single_employee,
        "all": get_all_employees
    },
    "customers": {
        "single": get_single_customer,
        "all": get_all_customers
    }
}
# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.


class HandleRequests(BaseHTTPRequestHandler):
    # This is a Docstring it should be at the beginning of all classes and functions
    # It gives a description of the class or function
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    def get_all_or_single(self, resource, id):
        """DRY method for all or single resource."""
        if id is not None:
            response = method_mapper[resource]["single"](id)

            if response is not None:
                self._set_headers(200)
            else:
                self._set_headers(404)
                response = {"message": f"{resource} {id} does not exist."}
        else:
            self._set_headers(200)
            response = method_mapper[resource]["all"]()

        return response

    def do_GET(self):
        """Get for query string parameters"""
        self._set_headers(200)

        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)
        ( resource, id, query_params ) = parsed

        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            if resource == "animals":
                if id is not None:
                    response = get_single_animal(id)
                else:
                    response = get_all_animals(query_params)
            elif resource == "customers":
                if id is not None:
                    response = get_single_customer(id)
                else:
                    response = get_all_customers()
            elif resource == "locations":
                if id is not None:
                    response = get_single_location(id)
                else:
                    response = get_all_locations()
            elif resource == "employees":
                if id is not None:
                    response = get_single_employee(id)
                else:
                    response = get_all_employees()

        else: # There is a ? in the path, run the query param functions
            (resource, id, query_params) = parsed

            # see if the query dictionary has an email key
            if query_params.get('email') and resource == 'customers':
                response = get_customer_by_email(query_params['email'][0])
            if query_params.get('location_id') and resource == 'employees':
                response = get_employees_by_location(query_params['location_id'][0])
            if query_params.get('location_id') and resource == 'animals':
                response = get_animals_by_location(query_params['location_id'][0])
            if query_params.get('status') and resource == 'animals':
                response = get_animal_by_status(query_params['status'][0])

        self.wfile.write(json.dumps(response).encode())

    # def do_GET(self):
    #     "GET function to cover all resources"
    #     response = None
    #     (resource, id) = self.parse_url(self.path)
    #     response = self.get_all_or_single(resource, id)
    #     self.wfile.write(json.dumps(response).encode())

    # Here's a class function
    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    # def do_GET(self):
    #     """Handles GET requests to the server
    #     """
    #     # Set the response code to 'Ok'
    #     response = {}

    #     # Parse the URL and capture the tuple that is returned
    #     (resource, id) = self.parse_url(self.path)

    #     if resource == "animals":
    #         if id is not None:
    #             response = get_single_animal(id)
    #             if response is not None:
    #                 self._set_headers(200)
    #             else:
    #                 self._set_headers(404)
    #                 response = { "message": f"Animal {id} can't deal with you right now." }
    #         else:
    #             self._set_headers(200)
    #             response = get_all_animals()

    #     if resource == "locations":
    #         if id is not None:
    #             response = get_single_location(id)
    #             if response is not None:
    #                 self._set_headers(200)
    #             else:
    #                 self._set_headers(404)
    #                 response = { "message": f"Location {id} does not exist." }
    #         else:
    #             self._set_headers(200)
    #             response = get_all_locations()

    #     if resource == "employees":
    #         if id is not None:
    #             response = get_single_employee(id)
    #             if response is not None:
    #                 self._set_headers(200)
    #             else:
    #                 self._set_headers(404)
    #                 response = { "message": f"Employee {id} does not exist." }
    #         else:
    #             self._set_headers(200)
    #             response = get_all_employees()

    #     if resource == "customers":
    #         if id is not None:
    #             response = get_single_customer(id)
    #             if response is not None:
    #                 self._set_headers(200)
    #             else:
    #                 self._set_headers(404)
    #                 response = { "message": f"Customer {id} does not exist." }
    #         else:
    #             self._set_headers(200)
    #             response = get_all_customers()

    #     self.wfile.write(json.dumps(response).encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        """Create New Animal."""
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, _, _) = self.parse_url(self.path)

        # Initialize new animal
        new_animal = None

        # Add a new animal to the list.
        if resource == "animals":
            if "name" in post_body and "breed" in post_body and "status" in post_body and "location_id" in post_body and "customer_id" in post_body:
                self._set_headers(201)
                new_animal = create_animal(post_body)
            else:
                self._set_headers(400)
                new_animal = {"message": f'{"name is required" if "name" not in post_body else ""} {"status is required" if "status" not in post_body else ""}{"location id is required" if "location_id" not in post_body else ""}{"customer id is required" if "customer_id" not in post_body else ""}'}
        # Encode the new animal and send in response
            self.wfile.write(json.dumps(new_animal).encode())

        new_location = None
        if resource == "locations":
            if "name" in post_body and "address" in post_body:
                self._set_headers(201)
                new_location = create_location(post_body)
            else:
                self._set_headers(400)
                new_location = {
                    "message": f'{"name is required" if "name" not in post_body else ""} {"address is required" if "address" not in post_body else ""}'}
            self.wfile.write(json.dumps(new_location).encode())

        # Initialize new employee
        new_employee = None
        if resource == "employees":
            if "name" in post_body:
                self._set_headers(201)
                new_employee = create_employee(post_body)
            else:
                self._set_headers(400)
                new_employee = {
                    "message": f'{"name is required" if "name" not in post_body else ""}'}
            self.wfile.write(json.dumps(new_employee).encode())

        # Initialize new customer
        new_customer = None
        if resource == "customers":
            if "email" in post_body and "full_name" in post_body:
                self._set_headers(201)
                new_customer = create_customer(post_body)
            else:
                self._set_headers(400)
                new_customer = {
                    "message": f'{"email is required" if "email" not in post_body else ""} {"full name is required" if "full_name" not in post_body else ""}'}
            self.wfile.write(json.dumps(new_customer).encode())

    def do_DELETE(self):
        """To Delete Items."""
        # Set a 204 response code
        delete_customer = None
        # Parse the URL
        (resource, id, _) = self.parse_url(self.path)

        # Delete a single animal from the list
        if resource == "animals":
            self._set_headers(204)
            delete_animal(id)

        # Encode the new animal and send in response
            self.wfile.write("".encode())

        if resource == "locations":
            self._set_headers(204)
            delete_location(id)
            self.wfile.write("".encode())

        if resource == "employees":
            self._set_headers(204)
            delete_employee(id)
            self.wfile.write("".encode())

        if resource == "customers":
            self._set_headers(405)
            delete_customer = {
                "message": "Contact the company directly to delete."}
            self.wfile.write(json.dumps(delete_customer).encode())

    def do_PUT(self):
        """Edit for SQL database"""
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id, _) = self.parse_url(self.path)

        success = False

        if resource == "animals":
            success = update_animal(id, post_body)
        # rest of the elif's
        if resource == "locations":
            update_location(id, post_body)

        if resource == "employees":
            update_employee(id, post_body)

        if resource == "customers":
            update_customer(id, post_body)

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

        self.wfile.write("".encode())

    # def do_PUT(self):
    #     """Handles PUT requests to the server"""
    #     self._set_headers(204)
    #     content_len = int(self.headers.get('content-length', 0))
    #     post_body = self.rfile.read(content_len)
    #     post_body = json.loads(post_body)

    #     # Parse the URL
    #     (resource, id) = self.parse_url(self.path)

    #     # Delete a single animal from the list
    #     if resource == "animals":
    #         update_animal(id, post_body)

    #     if resource == "locations":
    #         update_location(id, post_body)

    #     if resource == "employees":
    #         update_employee(id, post_body)

    #     if resource == "customers":
    #         update_customer(id, post_body)

    #     # Encode the new animal and send in response
    #     self.wfile.write("".encode())

    def _set_headers(self, status):
        # This Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def parse_url(self, path):
        """Third tuple component for parsing url, id, and query_params"""
        url_components = urlparse(path)
        path_params = url_components.path.strip("/").split("/")
        query_params = []

        if url_components.query != '':
            query_params = url_components.query.split("&")

        resource = path_params[0]
        id = None

        try:
            id = int(path_params[1])
        except IndexError:
            pass  # No route parameter exists: /animals
        except ValueError:
            pass  # Request had trailing slash: /animals/

        return (resource, id, query_params)

    # replace the parse_url function in the class
    # def parse_url(self, path):
    #     """Parse the url into the resource and id"""
    #     parsed_url = urlparse(path)
    #     path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
    #     resource = path_params[1]

    #     if parsed_url.query:
    #         query = parse_qs(parsed_url.query)
    #         return (resource, query)

    #     pk = None
    #     try:
    #         pk = int(path_params[2])
    #     except (IndexError, ValueError):
    #         pass
    #     return (resource, pk)

    # def parse_url(self, path):
    #     """parsing"""
    #     # Just like splitting a string in JavaScript. If the
    #     # path is "/animals/1", the resulting list will
    #     # have "" at index 0, "animals" at index 1, and "1"
    #     # at index 2.
    #     path_params = path.split("/")
    #     resource = path_params[1]
    #     id = None

    #     # Try to get the item at index 2
    #     try:
    #         # Convert the string "1" to the integer 1
    #         # This is the new parseInt()
    #         id = int(path_params[2])
    #     except IndexError:
    #         pass  # No route parameter exists: /animals
    #     except ValueError:
    #         pass  # Request had trailing slash: /animals/

    #     return (resource, id)  # This is a tuple


# This function is not inside the class. It is the starting
# point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
