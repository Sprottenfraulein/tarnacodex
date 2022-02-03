import sqlite3


class DB:
    def __init__(self, table_name):
        self.conn = sqlite3.connect(table_name)
        self.cursor = self.conn.cursor()


