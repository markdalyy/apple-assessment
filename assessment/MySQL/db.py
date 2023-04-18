from mysql.connector import connect, Error
import os


class Database:
    def __init__(self, host, db, username, password):
        self.connection = connect(host=host, database=db, username=username, password=password)
        try:
            if self.connection.is_connected():
                print('connected')
        except Error as E:
            print('Error occurred', E)

    def execute_stmt(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            return 'Connection closed'
        else:
            return "No connection open :("


db = Database('127.0.0.1', 'cork_weather', 'mark', os.environ.get('MYSQL_PASS'))

# def test():
#    sql = "SELECT * from location"
#    print(db.execute_stmt(sql).fetchall())
#
# test()
