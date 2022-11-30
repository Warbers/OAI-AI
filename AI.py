import re
import math
from fuzzywuzzy import fuzz

class ai:
    def __init__(self, model, stop_words):
       self.model = model
       self.stop_words = []
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
        
        highest = max(self.answers, key=self.answers.get)
        total   = sum(self.answers.values())
        confidence = self.answers[highest] / total
         
        for answer in self.model["answers"]:
            if answer["id"] == highest:
                answer["keywords"] = keywords
                return answer, confidence
    
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

    DEFAULT_WEIGHT_CHANGE = 0.01
    def answer_feedback(self, answer_id, answer_good):
        if answer_good:
            move_weights_by = self.DEFAULT_WEIGHT_CHANGE
        else:
            move_weights_by = -self.DEFAULT_WEIGHT_CHANGE
        for weight in self.model["edges"]:
            if weight["answer_id"] == answer_id:
                x = weight["weight"]
                x = max(0, min(x, 1))
                # -x ** 2 + x makes a parabole from 0 to 1
                scale_weight = -x ** 2 + x
                weight["weight"] += move_weights_by * scale_weight
    
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
    locations = [
        "b14",
        "b16",
        "kantine",
        "kontor",
        "toilet"
    ]
    location_sentences = [
        "hvor er {}",
        "hvor kan jeg finde {}",
        "hvad er lokationen på {}",
        "hvor finder jeg {}",
        "hvor {}",
    ]
    misc_questions = [
        "hvordan søger jeg su",
        "hvor kan jeg søge su",
        "hvad kan jeg få i su",
        "hvad er su",
        "hvad er et su lån",
        "hvornår skal man betale su lån tilbage",
        "skal man betale su lån tilbage",
        "hvordan overlever man på 3000 om måneden",
        "hvad er der til frokost",
        "hvad er madplanen",
        "hvordan ser madplanen ud",
        "hvorfor laver kantinen madden så klamt",
        "hvordan overlever man på klam skolekantine mad",
        "hvor er McDonald's"
    ]
    import time
    from AI_loader import *

    model = load_model()

    stop_words = load_stop_words()

    test_ai = ai(model, stop_words)

    for sentence in location_sentences:
        for loc in locations:
            question = sentence.format(loc)
            answer, confidence = test_ai.get_answer(question)
            print(question)
            print(answer)
            print(confidence)
            print(test_ai.answers)
            feedback = answer["text"] == loc
            test_ai.answer_feedback(answer["id"], feedback)

    while True:
        inp = input("spørgsmål: ")
        if inp == "exit":
            break

        start = time.time()
        answer, confidence = test_ai.get_answer(inp)
        end = time.time()

        print(answer)
        print(confidence)
        benchmark_time_ms = (end - start) * 1000
        print(f"{benchmark_time_ms}ms")
        print(test_ai.answers)
        feedback = input("feedback [y/n]: ") == "y"
        test_ai.answer_feedback(answer["id"], feedback)

