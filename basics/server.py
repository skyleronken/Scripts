#!/usr/env/python


def start_server():

	run_server = True

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind((socket.gethostname(), 80))

	server_socket.listen(5)

	while run_server:
		(client_socket, address) = server_socket.accept()
		thread = client_thread(client_socket)
		thread.run()

def main():
	start_server();


if __name__ == "__main__":
    main()