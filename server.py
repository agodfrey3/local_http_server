import socket
import os
from pathlib import Path

LOCALHOST = "127.0.0.1"
PORT = 80
RECV_LEN = 4096

SUCCESS_CODE = 200
NOT_FOUND_CODE = 404

class WebServer(object):
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port

        # The server socket.
        self.__socket = None

        # The most recent client connected.
        self.__current_client = None

        # Number of bytes to receive.
        self.__recv_len = RECV_LEN

        # Current working directory. Used to find the necessary files.
        self.__cwd = os.getcwd()

    def start_server(self):
        self.__initialize_socket()
        self.__run_main_server_loop()

    def __initialize_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.__host, self.__port))
        sock.listen(5)
        self.__socket = sock

    def __run_main_server_loop(self):
        if self.__socket is None:
            raise AttributeError("Must call start_server() prior to running the main loop...")
        while True:
            client, address = self.__socket.accept()
            self.__current_client = client
            self.__handle_client(client)

    def __handle_client(self, client):
        data = client.recv(self.__recv_len)
        data = self.__format_payload(data)
        self.__parse_and_reply(data)

    @staticmethod
    def __format_payload(data):
        data = data.decode('ascii').split('\r\n')
        return data

    def __parse_and_reply(self, data):
        self.__parse(data)

    def __parse(self, data):
        tokens = data[0].split()

        # If we received an empty message.
        if len(tokens) < 3:
            return

        request_type = tokens[0]

        if request_type == 'GET':
            self.__process_get_request(tokens[1])
        else:
            raise NotImplementedError("Only GET requests are supported...")

    def __process_get_request(self, file_name: str):
        if file_name == '/':
            file_name = "index.html"

        # Sets successful status code to start.
        status_code = SUCCESS_CODE

        if not self.__file_exists(file_name):
            status_code = NOT_FOUND_CODE

        content_type = self.__lookup_content_type(file_name)
        if content_type is None:
            status_code = NOT_FOUND_CODE

        # Send header.
        self.__current_client.send(f"HTTP/1.1 {status_code} {self.__code_to_msg(status_code)}\r\n".encode('latin-1'))
        self.__current_client.send(f"Content-Type: {content_type}\r\n".encode('latin-1'))
        self.__current_client.send(f"Content-Length: {os.path.getsize(f'{self.__cwd}/{file_name}')}\r\n".encode('latin-1'))
        self.__current_client.send("\r\n".encode('latin-1'))

        # Send payload.
        if status_code == SUCCESS_CODE and content_type is not None:
            file = open(f"{self.__cwd}/{file_name}", 'rb')
            data = file.read()
            self.__current_client.send(data)
            file.close()

    def __file_exists(self, file_name):
        path = f"{self.__cwd}/{file_name}"
        return Path(path).exists()

    @staticmethod
    def __extract_content_type(data):
        for line in data:
            tokens = line.split()
            if "Accept:" in tokens[0]:
                return tokens[1].split(',')[0]
        return None

    @staticmethod
    def __lookup_content_type(filename):
        ext = filename.split(".")[-1]
        if ext in ['html']:
            return "text/html"
        elif ext in ['css']:
            return "text/css"
        elif ext in ['png']:
            return "image/png"
        elif ext in ['mp4']:
            return "video/mpeg"
        elif ext in ['js']:
            return 'application/javascript'
        elif ext in ['io']:
            return "image/x-icon"
        else:
            return None

    @staticmethod
    def __code_to_msg(code):
        if code == SUCCESS_CODE:
            return "OK"
        elif code == NOT_FOUND_CODE:
            return "NOT FOUND"
        else:
            return "UNK"


def main():
    web_server = WebServer(LOCALHOST, PORT)
    web_server.start_server()


if __name__ == '__main__':
    main()
