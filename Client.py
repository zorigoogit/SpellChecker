import time
import socket
import json

def client():
    host = '127.0.0.1'  # The server's hostname or IP address
    port = 65434  # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        while True:
            try:

                input_file = input("Enter file name: ")
                num_threads = input("Number of slaves(threads): ")

                start_time = time.time()

                input_params = json.dumps({"input_file": input_file, "num_threads": int(num_threads)})

                client_socket.send(input_params.encode('utf-8'))
                buffer_size = 1024 * 1024 # maximun 1mb data can be recieved.
                response = client_socket.recv(buffer_size).decode('utf-8')

                #print(response)

                response = json.loads(response)

                print(".......................................................")

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
            except Exception as e:
                
                print(f"ERROR: {e}")
                print("------------------------------------------------------\n")
            
if __name__ == "__main__":
    client()