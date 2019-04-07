import sqlite3


class DBManager():
    def __init__(self):
        self.conn = sqlite3.connect('video_stats.db')

    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS requests (
                             id integer PRIMARY KEY,
                             date DATETIME DEFAULT (datetime('now','localtime')),
                             url text,
                             user text);
                            """
                          )
        self.conn.execute("""CREATE TABLE IF NOT EXISTS uploaded_files (
                                 id integer PRIMARY KEY,
                                 url text,
                                 file_id text);
                                """
                          )

    def insert_file_id(self, url, file_id):
        cur = self.conn.cursor()
        sql = """INSERT INTO uploaded_files(url, file_id) VALUES(?,?)"""
        cur.execute(sql, (url, file_id))
        self.conn.commit()

    def insert_user_request(self, url, username):
        cur = self.conn.cursor()
        sql = """INSERT INTO requests(url,user)
                          VALUES(?,?);"""
        cur.execute(sql, (url, username))
        self.conn.commit()

    def get_url_file_id(self, url):
        file_id = self.conn.execute("""SELECT file_id FROM uploaded_files WHERE url=?""", (url,)).fetchone()
        if file_id:
            return file_id[0]
        return None
