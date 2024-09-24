import socket


def setup_tcp_client(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 12345))
    print(f"Клиент подключен с адресом: {client_socket.getsockname()}")

    print(f"Отправка сообщения: {message}")
    client_socket.sendall(message.encode())

    response = client_socket.recv(1024)
    print(f"Ответ от сервера: {response.decode()}")

    client_socket.close()


if __name__ == "__main__":
    message = "Привет, TCP-сервер!"
    setup_tcp_client(message)
