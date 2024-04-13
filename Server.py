import socket
import threading
import json
import queue
import string
import os


def preprocess_line(line):

    allowed_chars = "'-"
    not_allowed_chars = ''.join(c for c in string.punctuation if c not in allowed_chars)
    translator = str.maketrans('', '', not_allowed_chars)

    line = line.translate(translator)
    return line.strip().lower()

def num_unique_chars(word1, word2):
    word1_unique = [x for x in list(word1) if x not in list(word2)]
    word2_unique = [x for x in list(word2) if x not in list(word1)]
    return len(word1_unique) + len(word2_unique)    
    
def word_cmp(word1, word2):
    if word1 == word2:
        return 0
    if word1[0] != word2[0]:
        return 100

    average_word_len = (len(word1) + len(word2))/2

    return int(num_unique_chars(word1, word2) / average_word_len * 100)


def producer(input_queue, misspelled_words, thread_id):
    while True:
       
        line = input_queue.get()        ###
        if line is None:                ###
            input_queue.task_done()
            break    

        line_No = line["line_no"]
        line_data = line["line_data"]
       
        line_data = preprocess_line(line_data)    
       
        for word in line_data.split():
            word_found = False
            min_diff = 100
            suggestion_word = "no suggestion"
            with open("dictionary1.txt", 'r') as dictionary_file:
                for dictionary_word in dictionary_file:
                    dictionary_word = dictionary_word.strip().lower()

                    if dictionary_word == word:
                        word_found = True
                        break
                    diff = word_cmp(word, dictionary_word)
                    if min_diff > diff:
                        min_diff = diff
                        suggestion_word = dictionary_word
            if not word_found:         
                misspelt_word = {
                                    "line_number": line_No, 
                                    "misspelt_word": word, 
                                    "suggestion_word": suggestion_word
                                }
                misspelled_words.append(misspelt_word)   
        input_queue.task_done()
        print(f"Thread {thread_id} : performed line - {line_No}")

def handle_client(client_socket, client_address):
    try:
        while True:
            
            client_request = client_socket.recv(1024).decode('utf-8')
            if not client_request:
                break

            client_request = json.loads(client_request)            
            
            print(f"{client_address} client request: {client_request}")
            
            ret_value ={"STATUS": "OK"}

           
            misspelled_words = []

            input_queue = queue.Queue()
            input_file_name = client_request["input_file"]
            num_threads = client_request["num_threads"]

            if not os.path.exists(input_file_name):
                ret_value["STATUS"] = "ERROR"
                ret_value["VALUE"] = "File not found!"

                response = json.dumps(ret_value)
                client_socket.send(response.encode('utf-8'))
                print(f"{client_address} client response: Error - File not found!")
                continue
            
            
           
            threads = []
            for i in range(num_threads):
                t = threading.Thread(target=producer, args=(input_queue, misspelled_words, i+1))
                t.start()
                threads.append(t)            

           
            with open(input_file_name, 'r') as input_file:
                line_number = 0
                for line_data in input_file:
                    line_number += 1
                    line = {
                                "line_no": line_number, 
                                "line_data" : line_data
                           }
                    input_queue.put(line)

            # Block until all tasks are done
            input_queue.join()
            
            # Stop produces threads
            for _ in range(num_threads):
                input_queue.put(None)
            for t in threads:
                t.join()

            ret_value["VALUE"] = misspelled_words
            response = json.dumps(ret_value)

            client_socket.send(response.encode('utf-8'))

            print(f"{client_address} client response: In total, {len(misspelled_words)} misspelled words with their suggested corrections were sent.")
            
            
    except Exception as e:
        print(f"Error in Client handle: {e}")
    finally:
        client_socket.close()

def main():
    host = '127.0.0.1'  
    port = 65434  

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
    main()
