import socket


AMOUNT_OF_CLIENTS = 1


def setup_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12345))
    server_socket.listen(AMOUNT_OF_CLIENTS)  # Ожидание подключений
    print(
        f"TCP сервер запущен на порту 12345. Ожидание подключения, максимальное количество = {AMOUNT_OF_CLIENTS}..."
    )

    while True:
        client_socket, address = server_socket.accept()
        print(f"Подключен клиент: {address}")
        handle_client(client_socket)
        
        # Если раскоментировать, то будет обрабатывать лишь одно сообщение
        # server_socket.close()
        # break


def handle_client(client_socket):
    data = client_socket.recv(1024)
    print(f"Получено сообщение: {data.decode()}")
    client_socket.sendall(data)
    print(f"Сообщение отправлено обратно.")
    client_socket.close()
    print(f"Соединение с клиентом закрыто.")


if __name__ == "__main__":
    setup_tcp_server()
