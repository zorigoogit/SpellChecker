import time
import socket
import json

def client():
    host = '127.0.0.1'  # The server's hostname or IP address
    port = 65432  # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        while True:
            message = input("Enter file name: ")
            start_time = time.time()

            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')

            response = json.loads(response)
            print("")
            if(response["STATUS"] =="OK"):
                misspelt_words = response["VALUE"]

                if (len(misspelt_words)):
                    print(f'{"Line No.":<10} {"Misspelt word":<30} {"Suggestion":<30}','\n')

                    for word in misspelt_words:
                        print(f'{word["line_number"]:<10} {word["misspelt_word"]:<30} {word["suggestion_word"]:<30}')
                else:
                    print("Miss-spelt words not found.")


            else:
                print(response["VALUE"])

            processing_time = time.time() - start_time 
            
            print(f"\nTotal processing time = {processing_time} seconds")  
            print("------------------------------------------------------\n")           

if __name__ == "__main__":
    client()