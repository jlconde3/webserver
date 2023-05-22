import socket
import logging

def main():

    #Set level for logging
    logging.basicConfig(level='DEBUG')


    #Set host and port for web server.
    HOST, PORT = '127.0.0.1',8889

    #Define liseting socket. This one is in charge of 
    #listeining reqeust connections and is not in charge of
    #sending and reciving data from the client.

    listen_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    listen_socket.bind((HOST,PORT))
    listen_socket.listen()
    logging.info(f'Web server running in http://{HOST}:{PORT}')

    try:
        while True:
            client_socket,client_address = listen_socket.accept()
            logging.info(f'Client connected!! Address:{client_address}')
            client_data = client_socket.recv(1024).decode('utf-8')
            parse_request(client_data)
            client_socket.sendall(b'HTTP/1.0 200 OK\r\nContent-Length: 11\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nHello World\r\n')
            client_socket.close()

    #In caso of keybord interruption by the user, we close the listing socket and set free for the system.
    except KeyboardInterrupt:
        listen_socket.close()


def parse_request(text:str):
    '''
    Example of a request. The important line is the first one.
    GET /hello HTTP/1.1
    Host: 127.0.0.1:8889
    .
    .
    .
    '''
    http_request = text.splitlines()[0]
    logging.debug(http_request)
    (method,path,request_version) = http_request.split()
    logging.info((method,path,request_version))

if __name__ == '__main__':
    main()


