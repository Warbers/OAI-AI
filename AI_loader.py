import mysql.connector
import json

def load_model():
    with open("dataconfig.json") as conf:
        config = json.load(conf)

    mydb = mysql.connector.connect(**config)
    
    model = {}
    mycursor = mydb.cursor()
    mycursor.execute("SELECT Id, word FROM Keyword")
    model["keywords"] = [{"id": id, "word": word} for id, word in mycursor.fetchall()]

    mycursor.execute("SELECT Id, AnswerType, Text, State FROM Answer")
    model["answers"] = [{"id": id, "type": answer_type, "text": text, "state": state} for id, answer_type, text, state in mycursor.fetchall()]

    mycursor.execute("SELECT AnswerId, KeywordId, Weight FROM Answer_Keyword")
    model["edges"] = [{"answer_id": answer_id, "keyword_id": keyword_id, "weight": weight} for answer_id, keyword_id, weight in mycursor.fetchall()]

    mycursor.close()
    mydb.close()
    return model

def load_stop_words():
    stop_words = []
    stop_words_file = open("StopWords.csv", 'r')
    
    stop_words = stop_words_file.read().splitlines()

    return stop_words

if __name__ == "__main__":
    model = load_model()

    print(model)

    with open("model.json", "w") as model_file:
        json.dump(model, model_file, indent=4)
