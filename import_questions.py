import json
import psycopg2.extras

DB_HOST = "localhost"
DB_NAME = "identree"
DB_USER = "postgres"
DB_PASS = "Gamechanger"

def populate_questions_table():
    try:
        # Read JSON data from the file
        with open('questions.json', 'r') as json_file:
            question_data = json.load(json_file)
            # print(question_data)

        # Update question records in the database
        try:
            conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
            print("Connection successful")
        except psycopg2.Error as e:
            print(f"Database connection failed: {e}")

        cursor = conn.cursor()

        for question in question_data:
            cursor.execute("""
                UPDATE questions
                SET question = %s,
                    description = %s,
                    image_path = %s,
                    options = %s,
                    correct_option = %s,
                    explanation = %s
                WHERE id = %s
            """, (question['question'], question['description'], question['image_path'],
                json.dumps(question['options']), question['correct_option'], question['explanation'], question['question_id']))

        conn.commit()
        conn.close()
        print('SQL statement:', cursor.query)  # Print the executed SQL statement
        print("Questions updated successfully")
    except Exception as e:
        conn.rollback()  # Rollback changes in case of an error
        print('Error:', str(e))
    finally:
        conn.close() 

populate_questions_table()