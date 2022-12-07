import re
import math
from fuzzywuzzy import fuzz

class ai:
    def __init__(self, model, stop_words):
       self.model = model
       self.stop_words = stop_words
       self.answers = {}
       self.previous_questions = []

    # get an answer from a question
    classmethod
    def get_answer(self, question):
        keywords = []

        self.reset_answer()
        
        # clean the string and split on whitespace
        question = re.sub('[^a-zA-Z0-9 ]', '', question)
        words = question.lower().split()

        # remove common words (stop words)
        for stop_word in self.stop_words:
            if stop_word in words: words.remove(stop_word)

        # remove duplicate words
        words = list(dict.fromkeys(words))

        # process each word
        for word in words:
            keywords.append(self.process_word(word))
        
        # calculate the highest probability answer
        # and calculate the confidence
        highest = max(self.answers, key=self.answers.get)
        total   = sum(self.answers.values())
        if total != 0:
            confidence = self.answers[highest] / total
        else:
            confidence = 0
         
        for answer in self.model["answers"]:
            if answer["id"] == highest:
                new_question_id = len(self.previous_questions) + 1
                self.previous_questions.append({"question_id": new_question_id, "keywords": keywords, "answer_id": answer["id"]})
                answer["keywords"] = keywords
                self.add_new_keywords(answer, keywords)
                return answer, confidence, new_question_id
        
        # TODO: Should throw?
    
    # This value is purely based in trial and error
    MATCH_THRESHOLD = 0.7

    classmethod
    def process_word(self, word):
        good_keyword = ""
        best_match_precent = 0

        for keyword in self.model["keywords"]:
            # try to match the word
            match_precent = self.match_words(word, keyword["word"])

            # if the word matches better than previous...
            if match_precent > best_match_precent:
                good_keyword = keyword["word"]
                best_match_precent = match_precent

            # TODO: should this be outside the for-loop since it will run if later matches also reach 0.7
            # example: [0.7,0.8,0.9,1.0] will all make the weight go up
            if match_precent >= self.MATCH_THRESHOLD:
                for answer in self.model["edges"]:
                    if answer["keyword_id"] == keyword["id"]:
                        # add value based on the match_percent and an "activation function"
                        weight = self.calculate_weight_defensive(answer["weight"], match_precent)
                        self.answers[answer["answer_id"]] += weight

        # if the word reached our match threshold
        if best_match_precent >= self.MATCH_THRESHOLD:
            return good_keyword
        else:
            return word

    DEFAULT_WEIGHT_CHANGE = 0.1
    def answer_feedback(self, question_id, answer_good):
        if answer_good:
            move_weights_by = self.DEFAULT_WEIGHT_CHANGE
        else:
            move_weights_by = -self.DEFAULT_WEIGHT_CHANGE
        for question in self.previous_questions:
            if question["question_id"] == question_id:
                for keyword in question["keywords"]:
                    for edge in self.model["edges"]:
                        for real_keyword in self.model["keywords"]:
                            # TODO: FIX!
                            if edge["keyword_id"] == real_keyword["id"] and real_keyword["word"] == keyword and edge["answer_id"] == question["answer_id"]:
                                x = edge["weight"]
                                x = max(0, min(x, 1))
                                # -x^2 + x makes a parabola from 0 to 1
                                scale_weight = -x ** 2 + x
                                edge["weight"] += move_weights_by * scale_weight
    
    def add_new_keywords(self, answer, words):
        new_words = []
        for word in words:
            word_new = True
            for val in self.model["keywords"]:
                word_new = word_new and word != val["word"]
            if word_new:
                new_words.append(word)
        for word in new_words:
            k_id = len(self.model["keywords"]) + 1
            self.model["keywords"].append({"id": k_id, "word": word})
            self.model["edges"].append({"answer_id": answer["id"], "keyword_id": k_id, "weight": 0.5})

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
        return weight * (match_percent - 0.7) / 0.3

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
        "hvor er McDonald's"
    ]
    import time
    from ai_loader import *

    model = load_model()

    stop_words = load_stop_words()

    test_ai = ai(model, stop_words)

    for sentence in location_sentences:
        for loc in locations:
            question = sentence.format(loc)
            answer, confidence, q_id = test_ai.get_answer(question)
            print(question)
            print(answer)
            print(confidence)
            print(test_ai.answers)
            feedback = answer["text"] == loc
            test_ai.answer_feedback(q_id, feedback)

    while True:
        inp = input("spørgsmål: ")
        if inp == "exit":
            break

        start = time.time()
        answer, confidence, _ = test_ai.get_answer(inp)
        end = time.time()

        print(answer)
        print(confidence)
        benchmark_time_ms = (end - start) * 1000
        print(f"{benchmark_time_ms}ms")
        print(test_ai.answers)
        feedback = input("feedback [y/n]: ") == "y"
        test_ai.answer_feedback(answer["id"], feedback)
        print(test_ai.model["keywords"])
