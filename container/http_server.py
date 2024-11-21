from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import code_runner
import os

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            json_data = json.loads(post_data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            code_runner_response = code_runner.executeCode([json_data['code']], json_data['input'])
            response = {
                "message": "JSON received",
                "result": f"{code_runner_response}"
            }
            self.wfile.write(json.dumps(response).encode())

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Invalid JSON"}
            self.wfile.write(json.dumps(response).encode())

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running http://{httpd.server_address[0]}:{port}')
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(os.getenv("CR_PORT", "8080"))
    run(port=port)
