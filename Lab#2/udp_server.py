import socket

def setup_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12345))
    print("UDP сервер запущен на порту 12345. Ожидание данных...")

    while True:
        data, address = server_socket.recvfrom(1024) 
        print(f"Получено сообщение от {address}: {data.decode()}")
        
        server_socket.sendto(data, address)
        print(f"Сообщение отправлено обратно.")
        
        # Если раскоментировать, то будет обрабатывать лишь одно сообщение
        # server_socket.close()
        # break

if __name__ == "__main__":
    setup_udp_server()
