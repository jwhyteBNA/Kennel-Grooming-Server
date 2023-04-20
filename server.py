import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from repository import all, retrieve, create, delete, update

method_mapper = {
    "animals": {
        "single": retrieve,
        "all": all,
    },
    "locations": {
        "single": retrieve,
        "all": all
    },
    "employees": {
        "single": retrieve,
        "all": all
    },
    "customers": {
        "single": retrieve,
        "all": all
    }
}

class HandleRequests(BaseHTTPRequestHandler):
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    def get_all_or_single(self, resource, id):
        """DRY method for all or single."""
        if id is not None:
            response = method_mapper[resource]["single"](resource, id)
            if response is not None:
                self._set_headers(200)
            else:
                self._set_headers(404)
                response = {"message": f"{resource} {id} does not exist."}
        else:
            self._set_headers(200)
            response = method_mapper[resource]["all"](resource)
        return response

    def do_GET(self):
        """GET for all or single"""
        response = None
        (resource, id) = self.parse_url(self.path)
        response = self.get_all_or_single(resource, id)
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Create New Resource."""
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        (resource, _) = self.parse_url(self.path)
        new_resource = None
        required_fields = {
            "animals": ["name", "species", "locationId", "customerId", "status"],
            "locations": ["name", "address"],
            "customers": ["email", "full_name"],
            "employees": ["name"]
        }

        if resource in required_fields:
            missing_fields = [
                field for field in required_fields[resource] if field not in post_body
            ]
            if not missing_fields:
                self._set_headers(201)
                new_resource = create(resource, post_body)
                self.wfile.write(json.dumps(new_resource).encode())
            else:
                self._set_headers(400)
                message = {"message": "".join(
                    [f"{field} is required" for field in missing_fields]
                )
                }
                self.wfile.write(json.dumps(message).encode())
        else:
            self._set_headers(400)
            message = {"message": "Resource not valid"}
            self.wfile.write(json.dumps(message).encode())

    def do_DELETE(self):
        """To Delete Items."""
        delete_customer = None
        (resource, id) = self.parse_url(self.path)

        if resource == "customers":
            self._set_headers(405)
            delete_customer = { "message": "Contact the company directly to delete customer." }
            self.wfile.write(json.dumps(delete_customer).encode())
        else:
            self._set_headers(204)
            delete(resource, id)
            self.wfile.write("".encode())

    def do_PUT(self):
        """Handles PUT requests to the server"""
        self._set_headers(204)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        (resource, id) = self.parse_url(self.path)
        update(resource, id, post_body)
        self.wfile.write("".encode())

    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
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
        """parsing"""
        # Just like splitting a string in JavaScript. If the
        # path is "/animals/1", the resulting list will
        # have "" at index 0, "animals" at index 1, and "1"
        # at index 2.
        path_params = path.split("/")
        resource = path_params[1]
        id = None

        # Try to get the item at index 2
        try:
            # Convert the string "1" to the integer 1
            # This is the new parseInt()
            id = int(path_params[2])
        except IndexError:
            pass  # No route parameter exists: /animals
        except ValueError:
            pass  # Request had trailing slash: /animals/

        return (resource, id)  # This is a tuple


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
