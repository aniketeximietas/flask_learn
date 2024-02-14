import faiss
from sentence_transformers import SentenceTransformer
import sqlite3
model_name = "paraphrase-MiniLM-L6-v2"
model= SentenceTransformer(model_name)

###Read Faiss Index####
# i1 = faiss.read_index("faiss.index_v1")

###Make SQL Connection###
conn= sqlite3.connect("cache_answers.db")
cursor = conn.cursor()
query= "Select * from cache_answers"
cursor.execute(query)

tables = cursor.fetchall()

# all_records = cursor.fetchall()

##Actual Retrieval step###
# query= "What is meant by the data of my folio will be overwritten by current data?"
# temp=model.encode(query)
# temp = temp.reshape(-1,384)


# dist,ind= i1.search(temp,k=1)
# print(tables[ind[0][0]][1])### This will be the answer to be sent to user

# query= f"SELECT * FROM cache_answers WHERE id={ind[0][0]+1}"
# cursor.execute(query)
# record = cursor.fetchone()
# print("~~~~~~~~~~~",record[2])


####How to create Faiss Index####
lst_questions=[]
for idx, tab in enumerate(tables):
    temp= model.encode(tab[1])
    temp = temp.reshape(-1,384)
    lst_questions.append(temp)

index = faiss.IndexFlatL2(384)
for idx,quest in enumerate(lst_questions):
    index.add(quest)

faiss.write_index(index, "faiss.index_v1")