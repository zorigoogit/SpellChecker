import time
import string

class SpellChecker:
    
    def preprocess_line(self, line):

        allowed_chars = "'-"
        not_allowed_chars = ''.join(c for c in string.punctuation if c not in allowed_chars)
        translator = str.maketrans('', '', not_allowed_chars)

        line = line.translate(translator)
        return line.strip().lower()

    def num_unique_chars(self, word1, word2):
        word1_unique = [x for x in list(word1) if x not in list(word2)]
        word2_unique = [x for x in list(word2) if x not in list(word1)]
        return len(word1_unique) + len(word2_unique)    
        
    def word_cmp(self, word1, word2):
        if word1 == word2:
            return 0
        if word1[0] != word2[0]:
            return 100

        average_word_len = (len(word1) + len(word2))/2

        return int(self.num_unique_chars(word1, word2) / average_word_len * 100)

    def main(self, input_file_path, dictionary_file_path):
        ret_value ={"STATUS": "OK"}
        
        try:
            misspelt_words =[]

            # open input file
            with open(input_file_path, 'r') as input_file:
                # read line from file
                line_number=0

                for line in input_file:
                    line_number += 1
                    # preprocess line
                    line = self.preprocess_line(line)
                    
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
                                diff = self.word_cmp(word, dictionary_word)
                                if min_diff > diff:
                                    min_diff = diff
                                    suggestion_word = dictionary_word
                        if not word_found:
                            #print(f'{line_number:<10} {word:<30} {suggestion_word:<30}')                     
                            misspelt_word = {
                                                "line_number": line_number, 
                                                "misspelt_word": word, 
                                                "suggestion_word": suggestion_word
                                            }
                            misspelt_words.append(misspelt_word)   
            ret_value["VALUE"] = misspelt_words
        except FileNotFoundError:
            ret_value["STATUS"] ="ERROR"
            ret_value["VALUE"] = "File not found!"         
        except Exception as e: 
            ret_value["STATUS"] ="ERROR"
            ret_value["VALUE"] = str(e)
           

        return ret_value
        


