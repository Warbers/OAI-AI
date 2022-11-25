import socket
import mysql.connector
import json
import math
from fuzzywuzzy import fuzz

BUFFER_SIZE = 1024

with open("dataconfig.json") as conf:
    config = json.load(conf)

mydb = mysql.connector.connect(**config)

def get_answer_from_question(question):
    #question = question.lower().split()
    num_questions = len(question)
    listformat = ",".join(["%s"]*num_questions)
    
    mycursor = mydb.cursor()
    mycursor.execute(f"""
                SELECT 
                    ans.Id AS AnswerId, 
                    ans.AnswerType AS AnswerType, 
                    ans.Text AS AnswerValue,
                    ans.state AS Status,
                    SUM(akw.Weight) AS weight_sum 
                FROM OAI.Keyword AS kw
                        INNER JOIN OAI.Answer_Keyword AS akw ON kw.Id = akw.KeywordId
                        INNER JOIN OAI.Answer AS ans ON akw.AnswerId = ans.Id
                WHERE kw.word IN ({listformat})
                    GROUP BY AnswerId
                    ORDER BY weight_sum DESC
                LIMIT 1;
    """, (question))
    
    answer_result = mycursor.fetchone()
    mycursor.close()
    return answer_result

def handle_question(conn):
    data = conn.recv(BUFFER_SIZE)
    question = json.loads(data)["question"]

    answer_id, answer_type, text, state, weight = get_answer_from_question(question)

    responseObj = {
        "AnswerId": answer_id,
        "AnswerType": answer_type,
        "AnswerValue": text,
        "Status": state,
        "weight": weight
    }

    conn.send(bytes(json.dumps(responseObj), "utf8"))
    conn.close()

def match_words(word1, word2):
    percent = fuzz.ratio(word1, word2)
    match_percent = prc / 100
    return match_procent

def calculate_weight_line(weight, match_percent):
    return weight * (2 * match_percent-1)

def calculate_weight_aggressive(weight, match_percent):
    return weight * (math.pow((match_percent-0.5),2) * 2 + 0.5)

def calculate_weight_defensive(weight, match_percent):
    return weight * (math.sqrt((match_percent-0.5)/2)+0.5)

while True:
    listen_ip = "0.0.0.0" #'192.168.1.135'
    listen_port = 8888

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listen_ip, listen_port))
    s.listen(1)

    print('Listening for client...')
    sockval = s.accept()
    conn, addr = sockval
    print('Connection address:', addr)
    handle_question(conn)