import time
import string

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


def main(input_file_path, dictionary_file_path):
    start_time = time.time()
    
    # open input file
    with open(input_file_path, 'r') as input_file:
        # read line from file
        line_number=0

        print(f'{"Line No.":<10} {"Misspelt word":<30} {"Suggestion":<30}','\n') 
        for line in input_file:
            line_number += 1
            # preprocess line
            line = preprocess_line(line)
            
            for word in line.split():
                word_found = False
                min_diff = 100
                suggestion_word = "no suggestion"
                with open(dictionary_file_path, 'r') as dictionary_file:
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
                    print(f'{line_number:<10} {word:<30} {suggestion_word:<30}')      

    processing_time = time.time() - start_time
    print(f"Total processing time = {processing_time} seconds")             


if __name__ == '__main__':
    # Example usage
    main('input.txt', 'dictionary.txt')