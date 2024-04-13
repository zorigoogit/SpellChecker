"""
This application implements the client's logic to interact with a server over network sockets.
Key Features:
    - Configuration management via external JSON file for flexible network settings
    - User input for dynamic request parameters (file name and number of threads)
    - JSON serialization for structured request/response exchange with the server
    - Employs synchronous communication, waiting for server responses to proceed
    - Processes and displays the server's response, highlighting error handling and result presentation.
    - Measures and reports the processing time for user requests, focusing on performance.
Expertise and Highlights:
    - Robust network communication using socket programming.
    - Effective error handling mechanisms.
    - Adherence to distributed systems principles with focus on reliability and user experience.

GitHub Repository Link: https://github.com/zorigoogit/SpellChecker.git
"""

import time
import socket
import json

# Load client configuration settings, such as server's IP address and port, from a JSON file.
def get_config():
    with open('client_config.json', 'r') as config_file:
        return json.load(config_file)
    
# Main functionality of the client application.
def client():
    config = get_config()

    host = config["host"]  # Server's hostname or IP address.
    port = config["port"]  # Server's port.

     
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

        # Connect to the server
        client_socket.connect((host, port))
        while True:
            try:
                # Prompt the user for input file name and the number of threads (slaves).
                input_file = input("Enter file name: ")
                num_threads = input("Number of slaves(threads): ")

                # Record the start time of the request.
                start_time = time.time()

                # Prepare(serialize) and send the input parameters to the server.
                input_params = json.dumps({"input_file": input_file, "num_threads": int(num_threads)})
                client_socket.send(input_params.encode('utf-8'))
                
                buffer_size = config["buffer_size"] 
                # Receive the server's response.
                response = client_socket.recv(buffer_size).decode('utf-8')

                #print(response)

                response = json.loads(response)

                print(".......................................................")

                 # Process the response from the server.
                if(response["STATUS"] =="OK"):
                    misspelt_words = response["VALUE"]

                    # Display the misspelt words and their suggestions if any.
                    if (len(misspelt_words)):
                        print(f'{"Line No.":<10} {"Misspelt word":<30} {"Suggestion":<30}','\n')

                        for word in misspelt_words:
                            print(f'{word["line_number"]:<10} {word["misspelt_word"]:<30} {word["suggestion_word"]:<30}')
                    else:
                        print("Miss-spelt words not found.")

                else:
                    # Display any errors returned by the server.
                    print(response["VALUE"])
                
                
                # Calculate and display the total processing time.
                processing_time = time.time() - start_time 
                
                print(f"\nTotal processing time = {processing_time} seconds")  
                print("------------------------------------------------------\n")           
            except Exception as e:
                print(f"ERROR: {e}")
                print("------------------------------------------------------\n")
            
if __name__ == "__main__":
    client()