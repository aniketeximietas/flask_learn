import sqlite3

# Source database
source_database_path = './instance/cache_answers.db'
source_connection = sqlite3.connect(source_database_path)
source_cursor = source_connection.cursor()

# Target database
target_database_path = './cache_answers.db'
target_connection = sqlite3.connect(target_database_path)
target_cursor = target_connection.cursor()

# Execute a query to retrieve data from the source table
source_cursor.execute("SELECT * FROM mira_faqs;")
data_to_insert = source_cursor.fetchall()

# Execute a query to create the target table in the target database (if it doesn't exist)
target_cursor.execute("""
    CREATE TABLE IF NOT EXISTS cache_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        password TEXT NOT NULL
    );
""")

# Execute a query to insert data into the target table
target_cursor.executemany(
    "INSERT INTO cache_answers (question,password) VALUES (?, ?);", data_to_insert)

# Commit the changes in the target database
target_connection.commit()

# Close the connections
source_connection.close()
target_connection.close()
