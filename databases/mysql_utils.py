import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

mysqlHost = os.getenv('MYSQL_HOST')
mysqlUser = os.getenv('MYSQL_USER')
mysqlPassword = os.getenv('MYSQL_PASSWORD')
mysqlDatabase = os.getenv('MYSQL_DATABASE')

def get_mysql():
    cnx = mysql.connector.connect(user=mysqlUser, password=mysqlPassword, database=mysqlDatabase)
    return cnx

if __name__ == "__main__":
    mysql = get_mysql()
    
class MySQL():
    def __init__(self):
        self.client = get_mysql()
        self.prepared_statement()
        # self.create_procedure()
        # self.add_constraint()
        # self.check()
        
    def prepared_statement(self):
        statement = 'SELECT * FROM keyword;'
        cnx = self.client
        cursor = cnx.cursor()
        query = "prepare getAllKeywords from 'SELECT * FROM keyword';"
        cursor.execute(query)
        
    def get_keywords(self):
        cnx = self.client
        cursor = cnx.cursor()
        
        cursor.execute('execute getAllKeywords;')
        
        keywords = []
        results = cursor.fetchall()
        for row in results:
            # print(row)
            keywords.append(row[1])
        cursor.close()
        return keywords
    
    def create_procedure(self):
        cursor = self.client.cursor()
        procedure_query = """
            CREATE PROCEDURE selectAllKeywords()
                SELECT * FROM keyword;
        """

        try:
            cursor.execute(procedure_query)
            cursor.close()
            print("Stored procedure created successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def check(self):
        connection = self.client
        if connection.is_connected():
            cursor = connection.cursor()

            # Check for existing rows that violate the constraint
            cursor.execute("""
                SELECT * FROM faculty
                WHERE NOT (
                    (email LIKE '%_@_%._%' AND
                     email NOT LIKE '@%' AND
                     email NOT LIKE '%@%@%')
                );
            """)
            rows = cursor.fetchall()

            if rows:
                print("There are rows that violate the constraint. Please correct or delete them before adding the constraint.")
                # for row in rows:
                #     print(row)
            else:
                # Add the constraint if no violating rows are found
                add_constraint_query = """
                ALTER TABLE faculty
                ADD CONSTRAINT emailcheck CHECK (
                    (email LIKE '%_@_%._%' AND
                     email NOT LIKE '@%' AND
                     email NOT LIKE '%@%@%')
                    OR email IS NULL
                );
                """
                cursor.execute(add_constraint_query)
                connection.commit()
                print("Constraint added successfully.")

    

