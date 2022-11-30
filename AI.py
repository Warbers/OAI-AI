import re
import math
from fuzzywuzzy import fuzz

class ai:
    def __init__(self, model, stop_words):
       self.model = model
       self.stop_words = stop_words
       self.answers = {}

    classmethod
    def get_answer(self, question):
        keywords = []

        self.reset_answer()
        
        question = re.sub('[^a-zA-Z0-9 ]', '', question)
        words = question.lower().split()

        for stop_word in self.stop_words:
            if stop_word in words: words.remove(stop_word)

        words = list(dict.fromkeys(words))

        for word in words:
            keywords.append(self.process_word(word))
        
        highest = max(self.answers, key=self.answers.get);
        
        for answer in self.model["answers"]:
            if answer["id"] == highest:
                answer["keywords"] = keywords
                return answer
    
    classmethod
    def process_word(self, word):
        good_keyword = ""
        best_match_precent = 0

        for keyword in self.model["keywords"]:
            match_precent = self.match_words(word, keyword["word"])

            if match_precent > best_match_precent:
                good_keyword = keyword["word"]
                best_match_precent = match_precent

            if match_precent >= 0.7:
                for answer in self.model["edges"]:
                    if(answer["keyword_id"] == keyword["id"]):
                        weight = self.calculate_weight_defensive(answer["weight"], match_precent)
                        self.answers[answer["answer_id"]] += weight

        if best_match_precent >= 0.7:
            return good_keyword
        else:
            return word
    
    def reset_answer(self):
        self.answers = {}
        for answer in self.model["answers"]:
            self.answers[answer["id"]] = 0.0

    def match_words(self, word1, word2):
        percent = fuzz.ratio(word1, word2)
        match_percent = percent / 100
        return match_percent
    
    def calculate_weight_simpleline(self, weight, match_percent):
        return weight * match_percent

    def calculate_weight_line(self, weight, match_percent):
        return weight * (3 * match_percent-2)

    def calculate_weight_aggressive(self, weight, match_percent):
        return weight * (math.pow((match_percent-0.7),2) * (10/3) + 0.7)

    def calculate_weight_defensive(self, weight, match_percent):
        return weight * (math.sqrt((match_percent-0.7)/(10/3) )+0.7)


if __name__ == "__main__":
    import time
    from AI_loader import *

    model = load_model()

    stop_words = load_stop_words()

    test_ai = ai(model, stop_words)

    inp = ""
    while(inp != "exit"):
        inp = input()

        start = time.time()
        answer = test_ai.get_answer(inp)
        end = time.time()

        print(answer)
        benchmark_time_ms = (end - start) * 1000
        print(f"{benchmark_time_ms}ms")
