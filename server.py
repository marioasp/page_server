import os
import socket
import threading
from urllib.parse import unquote

def handle_connection(client_connection, directory):
    request = client_connection.recv(1024).decode()
    headers = request.split('\n')
    if not headers or not headers[0]:
        client_connection.close()
        return
    request_line = headers[0].split()
    if len(request_line) < 2:
        client_connection.close()
        return
    filename = request_line[1]

    if filename == '/HEADER':
        response = 'HTTP/1.0 200 OK\n\n' + request
        client_connection.sendall(response.encode())
        client_connection.close()
    else:
        if filename == '/':
            filename = ''
        filepath = os.path.join(directory, unquote(filename[1:]))

        if os.path.isdir(filepath):
            response = 'HTTP/1.0 200 OK\n\n'
            for file in os.listdir(filepath):
                response += f'<a href="{filename}/{file}">{file}</a><br>'
            client_connection.sendall(response.encode())
            client_connection.close()
        else:
            try:
                with open(filepath, 'rb') as f:
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + f.read()
                    client_connection.sendall(response)
                    client_connection.close()
            except FileNotFoundError:
                response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
                client_connection.sendall(response.encode())
                client_connection.close()

def run_server(port, directory):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(1)

    while True:
        client_connection, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_connection, args=(client_connection, directory))
        thread.start()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1])
    directory = sys.argv[2]
    run_server(port, directory)
