import socket
import sys
import logging
import io 
from datetime import datetime


class WSGIServer(object):

    addres_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    requests_backlog = 1

    def __init__(self,server_address:tuple) -> None:
        self.listen_socket = listen_socket = socket.socket(
            self.addres_family,
            self.socket_type
        )

        listen_socket.bind(server_address)
        listen_socket.listen(self.requests_backlog)
        logging.debug(self.listen_socket.getsockname())

        host,port = self.listen_socket.getsockname()[:2]
        self.host = socket.getfqdn(host)
        self.port = port
        logging.info(f'Runnint server in http://{host}:{port}')

        self.headers_set = []

    def set_app(self,application):
        #Application develop using a web framework, in this case Flask. 
        self.application = application

    def serve_forever(self):
        try:
            while True:
                self.client_connection,self.client_address = self.listen_socket.accept()
                logging.info(f'Client connected to web server. Client address:{self.client_address}')
                #Method tha implement the logic for working with the requests
                self.handle_request()

            #In caso of keybord interruption by the user, we close the listing socket and set free for the system.
        except KeyboardInterrupt:
            self.listen_socket.close()

    def handle_request(self):
        self.client_request = client_request = self.client_connection.recv(1024).decode('utf-8')
        self.parse_request(client_request)
        #Logic with webframework
        env = self.get_environ()
        result = self.application(env,self.start_response)
        self.finish_response(result)
    
    def parse_request(self,text:str):
        '''
        Example of a request. The important line is the first one.

        GET /hello HTTP/1.1
        Host: 127.0.0.1:8889...
        '''

        http_request = text.splitlines()[0]
        (self.request_method,self.request_path,self.request_version) = http_request.split()
    
    def get_environ(self)->dict:
        env = {}

        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.client_request)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variables
        env['REQUEST_METHOD'] = self.request_method   
        env['PATH_INFO'] = self.request_path          
        env['SERVER_NAME'] = self.host       
        env['SERVER_PORT'] = str(self.port)
            
        return env

    def start_response(self,status,response_headers:list,exc_info=None)->None:
        server_headers = [
            ('Date',datetime.today().strftime('%y-%m-%d %H:%M:%S')),
            ('Server','WSGIServer 1.0'),
        ]
        self.headers_set = [status,response_headers + server_headers]

    
    def finish_response(self,result)->None:
        try:
            status_code,response_headers = self.headers_set
            response = f'HTTP/1.1 {status_code}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            
            response += '\r\n'
            for data in result:
                response += data.decode()
            
            logging.debug(response)
            response = response.encode()
            self.client_connection.sendall(response)

        finally:
            self.client_connection.close()
            

SERVER_ADDRESS = (HOST,PORT) = '127.0.0.1',8889

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')

    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()
