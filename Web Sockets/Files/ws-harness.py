#!/usr/bin/python3
import socket, ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from websocket import create_connection
from urllib.parse import parse_qs
import argparse
import os

LOOP_BACK_PORT_NUMBER = 8000

def FuzzWebSocket(fuzz_value):
    print(fuzz_value)
    ws.send(ws_message.replace("[FUZZ]", str(fuzz_value[0])))
    result = ws.recv()
    return result

def LoadMessage(file):
    file_contents = ""
    try:
        if os.path.isfile(file):
            with open(file, 'r') as f:
                file_contents = f.read()
    except Exception as e:
        print("Error reading file: %s" % file)
        print(e)
        exit()
    return file_contents

class myWebServer(BaseHTTPRequestHandler):
    
    # Handler for the GET requests
    def do_GET(self):
        qs = parse_qs(self.path[2:])
        fuzz_value = qs['fuzz']
        result = FuzzWebSocket(fuzz_value)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # In Python 3, you should encode the result before writing it
        self.wfile.write(result.encode('utf-8'))
        return

parser = argparse.ArgumentParser(description='Web Socket Harness: Use traditional tools to assess web sockets')
parser.add_argument('-u', '--url', help='The remote WebSocket URL to target.', required=True)
parser.add_argument('-m', '--message', help='A file that contains the WebSocket message template to send. Please place [FUZZ] where injection is desired.', required=True)
args = parser.parse_args()

ws_message = LoadMessage(args.message)

ws = create_connection(args.url, sslopt={"cert_reqs": ssl.CERT_NONE}, header={}, http_proxy_host="", http_proxy_port=8080)

try:
    # Create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', LOOP_BACK_PORT_NUMBER), myWebServer)
    print('Started httpserver on port ', LOOP_BACK_PORT_NUMBER)
    
    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
    ws.close()
