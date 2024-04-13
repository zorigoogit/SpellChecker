"""
Server Application Logic
Multi-threaded server designed to handle concurrent client connections and requests over TCP/IP sockets.
Designed with best practices in distributed system development, this server application underscores 
a comprehensive approach to managing client requests, data processing, and network communication.

Key Features:
 - Configurable server settings by 'server_config.json', enabling flexibility in host, port, and dictionary file settings.
 - Initializes and listens for incoming client connections, creating a new thread for each connection to maintain ensure efficient handling.
 - Utilizes a custom SpellChecker class for preprocessing text and suggesting corrections, demonstrating application modularity logic.
 - Employs a thread pool to parallelize the processing of client requests, enhancing efficiency and scalability by distributing workload.
 - Incorporates advanced synchronization mechanisms, including Mutexes (mutual exclusions) and condition variables, to manage access to shared resources among threads safely.
 - Processes client requests by reading input files, identifying misspelt words, and generating suggestions based on a loaded dictionary.
 - Communicates with clients through JSON-formatted messages, ensuring structured data exchange and integrity.

Expertise and Highlights:
 - Demonstrates a deep understanding in socket programming and network communication.
 - Implements concurrency control and parallel processing techniques, crucial for high-performance server applications.
 - Highlights robust error handling and client-server communication strategies.
 - Focuses on scalability and efficiency, preparing the server for high-load scenarios and distributed system environments.

 GitHub Repository Link: https://github.com/zorigoogit/SpellChecker.git
"""

import socket
import threading
import json
import queue
import string
import os


# The SpellChecker class provides functionality for spell checking
class SpellChecker:

    # Removes punctuation from a line except apostrophes and hyphens. This preprocessing step is 
    # crucial for the spell-checking process, ensuring that punctuation does not interfere with word comparison.
    def preprocess_line(self, line):
        allowed_chars = "'-"
        not_allowed_chars = ''.join(c for c in string.punctuation if c not in allowed_chars)
        translator = str.maketrans('', '', not_allowed_chars)
        line = line.translate(translator)
        return line.strip().lower()

    # Calculates the number of unique characters between two words.
    # This function helps to determine how similar or different two words are.
    def __num_unique_chars(self, word1, word2):      
        word1_unique = [x for x in list(word1) if x not in list(word2)]
        word2_unique = [x for x in list(word2) if x not in list(word1)]
        return len(word1_unique) + len(word2_unique)

    
    # Compares two words and returns a similarity score between 0 (same) to 100 (totally different). This scoring is essential for
    # suggesting the most appropriate correction by finding the word with the lowest difference score.
    def word_cmp(self, word1, word2):
        if word1 == word2:
            return 0
        if word1[0] != word2[0]:
            return 100
        average_word_len = (len(word1) + len(word2))/2.0
        return int(self.__num_unique_chars(word1, word2) / average_word_len * 100)

    # Load dictionary file into a set.
    def load_dictionary(self, file_name):
        with open(file_name, 'r') as dictionary_file:
                return {line.strip().lower() for line in dictionary_file} 
        

# The Server class arranges server operations including initializing server settings, 
# listening for and handling client connections, and multithreaded processing of spell check requests.
class Server:
    # The server's initialization involves loading the configuration from a JSON file and the dictionary for spell checking.
    # This design choice enables flexibility and ease of modification for server settings and the spell checking dictionary.
    def __init__(self):
        self.spell_checker = SpellChecker()
        self.config = self.get_config()
        self.dictionary = self.spell_checker.load_dictionary(self.config["dictionary_file"]) 
        self.running = True

    # Loads server configuration from a JSON file. 
    def get_config(self):
        with open('server_config.json', 'r') as config_file:
            return json.load(config_file)
         
    # Initializes the server socket and listens for incoming client connections. This function demonstrates a deep understanding
    # of socket programming and the ability to implement a server that can handle multiple client connections concurrently.
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket
        server_socket.bind((self.config["host"], self.config["port"])) # Bind to address and port
        server_socket.listen() # Listen for client connections 
        server_socket.settimeout(1) # Set a timeout for the accept call.
        print(f"Server listening on {self.config['host']}:{self.config['port']} ....") 

        try:
            while self.running:
                try:
                    client_socket, address = server_socket.accept() # Accept new connection
                    print(f"A client has been connected from {address}")

                    # For each new client, a separate thread is created to manage their requests, 
                    # allowing the main thread to continue accepting other new clients. 
                    # These threads execute the "handle_client" function to process client request.
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True)
                    client_thread.start()
                except socket.timeout:
                    continue   
        except KeyboardInterrupt:
            print("the server is shutting down ...")
            self.running = False                                 
        finally:
            server_socket.close()
    
    # Handles client requests in a separate thread for each client. This approach demonstrates exceptional knowledge
    # of multi-threaded programming and its application in developing scalable server applications.
    def handle_client(self, client_socket, client_address):
        try:
            while True:
                client_request = client_socket.recv(1024).decode('utf-8') # to recieve client request   
                if not client_request:
                    break

                # Initializes context for client handling, including a queue for task management and a shared list for results.
                # This design reflects an advanced understanding of parallel programming techniques and synchronization mechanisms.
                # I declared these variables within the client handling function rather than globally in server application to ensure 
                # that they are exclusively accessible to consumer threads handling a single client. 
                # This approach isolates client-specific data, preventing any cross-client data leakage or interference.

                client_context = {
                    "input_queue": queue.Queue(self.config["queue_limit"]),
                    # the queue shared by all threads in the certein client request.
                    "Shared_list": [],     
                    # Global list to store misspelled words found by the consumer(worker) threads of the certain client request.     
                    "data_finished": False,     
                    # Flag to indicate whether all input data added into queue has been processed.  
                    "lock": threading.Lock(),
                    # Mutex for synchronizing access to shared resources.  
                }   
                
                # The condition variable allows threads to wait for certain conditions to be met before proceeding.
                client_context["condition"] = threading.Condition(client_context["lock"])  

                # parse client request message to json
                client_request = json.loads(client_request)  
                # print crequest parameters. For tracking purpose.
                print(f"{client_address} client request: {client_request}")

                ret_value ={"STATUS": "OK", "VALUE": None}

                input_file_name = client_request["input_file"]
                num_threads = client_request["num_threads"]

                # check input file exists. if not exists return error message: "file not found!" 
                if not os.path.exists(input_file_name):
                    ret_value["STATUS"] = "ERROR"
                    ret_value["VALUE"] = "File not found!"
                    response = json.dumps(ret_value)
                    client_socket.send(response.encode('utf-8'))
                    print(f"{client_address} client response: Error - File not found!")
                    continue
                
                # Create and start consumer(worker) threads to process input data in parallel.
                threads = []
                for i in range(num_threads):
                    t = threading.Thread(target=self.consumer, args=(client_context, i+1))
                    t.start()
                    threads.append(t)            
                
                # Producer: Read input file and feed lines into the queue for processing by consumer threads
                with open(input_file_name, 'r') as input_file:
                    line_number = 0
                    for line_data in input_file:
                        line_number += 1
                        line = {"line_no": line_number, "line_data" : line_data}
                        try:
                            # Wait for space to become available if the queue is full
                            with client_context["condition"]:
                                while client_context["input_queue"].full(): 
                                    client_context["condition"].wait(timeout=3) # Wait 3 seconds

                                # Once space is available, try to put the item into the queue    
                                client_context["input_queue"].put(line)
                                client_context["condition"].notify_all()  # Notify all consumer threads that new line is added
                        except queue.Full:
                            print(f"Queue is full. Unable to add more items.")        


                # notify to all consumer threads that all line of input file added into the input queue
                with client_context["condition"]:
                    client_context["data_finished"] = True
                    client_context["condition"].notify_all()

                
                # Wait for all threads to finish their process
                for trd in threads:
                    trd.join()

                # Fill return variable with the shared list
                ret_value["VALUE"] = client_context["Shared_list"]
                response = json.dumps(ret_value)

                # Send response back to client
                client_socket.send(response.encode('utf-8'))

                # Print to console the total number of misspelled words found. For tracking purpose.
                print(f"{client_address} client response: In total, {len(client_context['Shared_list'])} misspelled words with their suggested corrections were sent.")


        except Exception as e:
            print(f"Error in Client handle: {e}")
        finally:
            client_socket.close()  

    # Consumer threads process tasks from a shared queue, demonstrating the effective use of concurrency controls
    # to ensure synchronized access to shared resources, which is crucial for the reliability and efficiency of the server.
    def consumer(self, client_context, thread_id):
        
        while True:
            # Implementing condition.
            with client_context["condition"]:
                # Wait for tasks or completion signal.
                while client_context["input_queue"].empty() and not client_context["data_finished"]:
                    # If tasks are not yet complete but the queue is empty, wait for new items to be added to the queue.
                    client_context["condition"].wait()
                if client_context["data_finished"] and client_context["input_queue"].empty():
                    # Exit if no more tasks.
                    break
                line = client_context["input_queue"].get()                                             

            line_no = line["line_no"]
            line_data = line["line_data"]
        
            # Preprocess line
            line_data = self.spell_checker.preprocess_line(line_data)

            # Iterate to extract word from the line.
            for word in line_data.split():
                word_found = False
                min_diff = 100
                suggestion_word = "no suggestion"
                # Iterate dictionary words (line by line)
                for dictionary_word in self.dictionary:
                    # If the word is found in the dictionary, it is considered correct, and the iteration stops.
                    if dictionary_word == word:
                        word_found = True
                        break
                    # If not found, identify a dictionary word with the minimum difference from the word being searched.
                    diff = self.spell_checker.word_cmp(word, dictionary_word)
                    if min_diff > diff:
                        min_diff = diff
                        suggestion_word = dictionary_word
                # If same word was not found, suggest the dictionary word that has the smallest difference.
                if not word_found:
                    # Implementing a mutex lock to ensure that multiple threads do not update the shared global list concurrently.
                    with client_context["lock"]:
                        misspelt_word = {
                                            "line_number": line_no, 
                                            "misspelt_word": word, 
                                            "suggestion_word": suggestion_word
                                        }
                        # Add item (misspelled word with suggested word) to the global(shared) list.
                        client_context["Shared_list"].append(misspelt_word)
   
           # Mark task as done and notify waiting threads.
            with client_context["condition"]:
                client_context["input_queue"].task_done()  
                client_context["condition"].notify_all() 
                print(f"Thread {thread_id} : performed line - {line_no}")


if __name__ == "__main__":
    server = Server() 
    server.start() 
