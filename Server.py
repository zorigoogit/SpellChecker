import socket
import threading
from SpellChecker import SpellChecker
import json
import os

def handle_client(client_socket, client_address):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            request = f"{client_address} request: {message}"
            print(request)

            spell_shecker = SpellChecker()

            misspelt_words = spell_shecker.main(message, 'dictionary.txt')

            response = json.dumps(misspelt_words)

            client_socket.send(response.encode('utf-8'))
            if misspelt_words['STATUS'] == "OK":
                print(f"{client_address} response: Sent")
            else:
                print(f"{client_address} response: {misspelt_words['VALUE']}")
            
    except Exception as e:
        print(f"Error in Client handle: {e}")
    finally:
        client_socket.close()

def server():
    host = '127.0.0.1'  
    port = 65432  

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        print(f"A client has been connected from {address}")
        thread = threading.Thread(target=handle_client, args=(client_socket,address))
        thread.start()

if __name__ == "__main__":
    server()
