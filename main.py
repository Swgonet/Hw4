import urllib.parse
from pathlib import Path
import mimetypes
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from threading import Thread
import socket
from datetime import datetime

HTTP_IP = '0.0.0.0'
HTTP_PORT = 3000
BASE_DIR = Path()
BUFFER_SIZE = 1024
SOCK_HOST = '127.0.0.1'
SOCK_PORT = 5000


class PetyaFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', status_code=404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        print(data)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCK_HOST, SOCK_PORT))
        client_socket.close()

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open (filename, 'rb') as f:
            self.wfile.write(f.read())
    
    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open (filename, 'rb') as f:
            self.wfile.write(f.read())

def save_data(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    print(parse_data)
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        date = str(datetime.now())
        result = {date: parse_dict}
        print(result)
        if os.path.exists('storage/data.json'):
            with open(f'storage/data.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
                history.update(result)
            with open(f'storage/data.json', 'w', encoding='utf-8') as ft: 
                json.dump(history, ft, ensure_ascii=False, indent=4)
        else:
            with open('storage/data.json', 'w') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
    except ValueError as er:
        logging.error(er)
    except OSError as err:
        logging.error(err)

def run_sock_serv(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info('Server socket runing')
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f'Socket recv {address}: {msg}')
            save_data(msg)
    except:
        server_socket.close()


def run_http_server(host, port):
    adress = (host, port)
    httpserv = HTTPServer(adress, PetyaFramework)
    logging.info('Server socket runing')
    try:
        httpserv.serve_forever()
    except:
        httpserv.server_close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    server = Thread(target=run_http_server, args=(HTTP_IP, HTTP_PORT))
    server.start()

    server_socket = Thread(target=run_sock_serv, args=(SOCK_HOST, SOCK_PORT))
    server_socket.start()
