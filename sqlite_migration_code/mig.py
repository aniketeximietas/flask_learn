import sqlite3
import json

# Read the JSON file
with open('data.json', 'r',encoding='utf-8') as file:
    data = json.load(file)

# Connect to the SQLite database
conn = sqlite3.connect('cache_answers.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cache_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    );
""")


# Insert data into the table
for item in data:
    cursor.execute('''
        INSERT INTO cache_answers (question, answer)
        VALUES (?, ?)
    ''', (item['question'], item['answer']))

# Commit the changes and close the connection
conn.commit()
conn.close()
