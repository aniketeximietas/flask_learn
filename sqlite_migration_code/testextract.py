import os
import sqlite3

# Function to parse questions and answers from text content
def parse_text_content(content):
    # Split the content based on '?'
    question_answer_pairs = content.split('?')
    # Remove any empty strings
    # question_answer_pairs = [pair.strip() for pair in question_answer_pairs if pair.strip()]
    return question_answer_pairs

# Function to process each text file
def process_text_file(file_path, cursor):
    with open(file_path, 'r') as file:
        content = file.read()
        question_answer_pairs = parse_text_content(content)
        print(question_answer_pairs)
        # Insert each question-answer pair into the database
        for pair in question_answer_pairs:
            # Assume pair is 'question:answer' format
            # question, answer = pair.split(':')
            # cursor.execute("INSERT INTO qa_table (question, answer) VALUES (?, ?);", (question.strip(), answer.strip()))
            cursor.execute("INSERT INTO cache_answers (question, answer) VALUES (?, ?);", (question_answer_pairs[0], question_answer_pairs[1]))

# Create or connect to the SQLite database
database_path = 'cache_answers.db'
connection = sqlite3.connect(database_path)
cursor = connection.cursor()

# Directory containing the text files
directory = './'

# Process each text file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)
        process_text_file(file_path, cursor)

# Commit the changes and close the connection
connection.commit()
connection.close()
