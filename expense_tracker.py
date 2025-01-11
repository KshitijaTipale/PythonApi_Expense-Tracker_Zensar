import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import mysql.connector
from datetime import datetime

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "karuna1864",
    "database": "expense_tracker"
}

# Function to establish a connection to the database


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Serialize datetime objects to ISO 8601 string format


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

# Recursively serialize datetime objects inside nested structures (e.g., lists, dictionaries)


def recursive_serialize(obj):
    if isinstance(obj, dict):
        return {key: recursive_serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [recursive_serialize(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# Request handler class to handle incoming requests


class RequestHandler(BaseHTTPRequestHandler):

    # Handle GET requests
    def do_GET(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Route: Get Users
            if self.path.startswith("/users/"):
                user_id = self.path.split("/")[-1]
                cursor.execute(
                    "SELECT * FROM Users WHERE UserID = %s", (user_id,))
                result = cursor.fetchone()
                if result is None:
                    self.send_error(404, "User Not Found")
                    return
            elif self.path == "/users":
                cursor.execute("SELECT * FROM Users")
                result = cursor.fetchall()

            # Route: Get Categories
            elif self.path.startswith("/categories/"):
                category_id = self.path.split("/")[-1]
                cursor.execute(
                    "SELECT * FROM Categories WHERE CategoryID = %s", (category_id,))
                result = cursor.fetchone()
                if result is None:
                    self.send_error(404, "Category Not Found")
                    return
            elif self.path == "/categories":
                cursor.execute("SELECT * FROM Categories")
                result = cursor.fetchall()

            # Route: Get Expenses
            elif self.path.startswith("/expenses/"):
                expense_id = self.path.split("/")[-1]
                cursor.execute(
                    "SELECT * FROM Expenses WHERE ExpenseID = %s", (expense_id,))
                result = cursor.fetchone()
                if result is None:
                    self.send_error(404, "Expense Not Found")
                    return
            elif self.path == "/expenses":
                cursor.execute("SELECT * FROM Expenses")
                result = cursor.fetchall()

            # Route: Get Expense Logs
            elif self.path.startswith("/logs/"):
                log_id = self.path.split("/")[-1]
                cursor.execute(
                    "SELECT * FROM ExpenseLogs WHERE LogID = %s", (log_id,))
                result = cursor.fetchone()
                if result is None:
                    self.send_error(404, "Log Not Found")
                    return
            elif self.path == "/logs":
                cursor.execute("SELECT * FROM ExpenseLogs")
                result = cursor.fetchall()

            else:
                # Invalid Route
                self.send_error(404, "Invalid Endpoint")
                return

            # Serialize datetime fields and send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Recursively serialize result to handle datetime objects
            serialized_result = json.dumps(recursive_serialize(result))
            self.wfile.write(serialized_result.encode())

        except Exception as e:
            # Handle Errors
            self.send_error(500, str(e))
        finally:
            cursor.close()
            conn.close()

    # Handle POST requests
    def do_POST(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Route: Insert User
            if self.path == "/users":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_data)

                cursor.execute(
                    "INSERT INTO Users (Name, Email) VALUES (%s, %s)",
                    (data["Name"], data["Email"])
                )
                conn.commit()
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"message": "User created successfully!"}).encode())

            # Route: Insert Category
            elif self.path == "/categories":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_data)

                cursor.execute(
                    "INSERT INTO Categories (CategoryName) VALUES (%s)",
                    (data["CategoryName"],)
                )
                conn.commit()
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"message": "Category created successfully!"}).encode())

            # Route: Insert Expense
            elif self.path == "/expenses":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_data)

                cursor.execute(
                    "INSERT INTO Expenses (UserID, CategoryID, Amount, ExpenseDate) VALUES (%s, %s, %s, %s)",
                    (data["UserID"], data["CategoryID"],
                     data["Amount"], data["ExpenseDate"])
                )
                conn.commit()
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"message": "Expense created successfully!"}).encode())

            # Route: Insert Expense Log
            elif self.path == "/logs":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_data)

                cursor.execute(
                    "INSERT INTO ExpenseLogs (ExpenseID, LogMessage) VALUES (%s, %s)",
                    (data["ExpenseID"], data["LogMessage"])
                )
                conn.commit()
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"message": "Log entry created successfully!"}).encode())

            else:
                # Invalid Route
                self.send_error(404, "Invalid Endpoint")
                return

        except Exception as e:
            # Handle Errors
            self.send_error(500, str(e))
        finally:
            cursor.close()
            conn.close()

# Function to run the HTTP server


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


# Main execution
if __name__ == "__main__":
    run()
