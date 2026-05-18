from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os  # Added to read environment variables from Render

# Render dynamically assigns a port via the PORT environment variable.
# If running locally, it will default to 8000.
PORT = int(os.environ.get("PORT", 8000))


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":
            self.path = "/home.html"

        try:

            if self.path == "/tasks":

                with open("tasks.json", "r") as file:
                    tasks = json.load(file)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps(tasks).encode())

                return

            file_path = self.path[1:]

            content_type = "text/html"

            if file_path.endswith(".css"):
                content_type = "text/css"

            elif file_path.endswith(".js"):
                content_type = "application/javascript"

            with open(file_path, 'rb') as file:

                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()

                self.wfile.write(file.read())

        except:

            self.send_response(404)
            self.end_headers()

            self.wfile.write(b'File not found')

    def do_POST(self):

        if self.path == "/add":

            content_length = int(self.headers['Content-Length'])

            body = self.rfile.read(content_length)

            data = json.loads(body)

            with open("tasks.json", "r") as file:
                tasks = json.load(file)

            tasks.append(data)

            with open("tasks.json", "w") as file:
                json.dump(tasks, file, indent=4)

            self.send_response(200)
            self.end_headers()


# CRITICAL CHANGE: Replacing 'localhost' with '' binds the server to 0.0.0.0.
# This opens the server up so Render's external load balancer can route web traffic into it.
server = HTTPServer(('', PORT), MyHandler)

print(f"Server running on port {PORT}...")

server.serve_forever()