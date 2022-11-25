import sys
import socket
from threading import Thread
import mysql.connector
import json

TCP_IP = "0.0.0.0" #'192.168.1.135'
TCP_PORT = 8888
BUFFER_SIZE = 1024
param = []
i=0

with open("dataconfig.json") as conf:
    config = json.loads(conf.read())

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

def HandleQuestion(conn):
    data = conn.recv(BUFFER_SIZE)
    question = json.loads(data)["question"]

    answerId, answerType, text, state, weight = get_answer_from_question(question)

    responseObj = {
        "AnswerId": answerId,
        "AnswerType": answerType,
        "AnswerValue": text,
        "Status": state,
        "weight": weight
    }

    conn.send(bytes(json.dumps(responseObj), "utf8"))
    conn.close()

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print('Listening for client...')
    sockval = s.accept()
    conn, addr = sockval
    print('Connection address:', addr)
    HandleQuestion(conn)