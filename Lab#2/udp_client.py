import socket


def setup_udp_client(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Отправка сообщения: {message}")
    client_socket.sendto(message.encode(), ("localhost", 12345))

    response, address = client_socket.recvfrom(1024)
    print(f"Ответ от сервера: {response.decode()}")

    client_socket.close()


if __name__ == "__main__":
    message = "Привет, UDP-сервер!"
    setup_udp_client(message)
