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
                                 quality text,
                                 file_id text);
                                """
                          )
        self.conn.execute("""CREATE TABLE IF NOT EXISTS settings (
                                 id integer PRIMARY KEY,
                                 chat_id text,
                                 quality text);
                                """
                          )

    def insert_file_id(self, url, file_id, quality='min'):
        cur = self.conn.cursor()
        sql = """INSERT INTO uploaded_files(url, file_id, quality) VALUES(?,?,?)"""
        cur.execute(sql, (url, file_id, quality))
        self.conn.commit()

    def create_new_user(self, chat_id):
        if self.get_chat_quality(chat_id):
            return
        cur = self.conn.cursor()
        sql = """INSERT INTO settings(chat_id,quality) VALUES(?, "min")"""
        cur.execute(sql, (chat_id,))
        self.conn.commit()

    def insert_user_request(self, url, username):
        cur = self.conn.cursor()
        sql = """INSERT INTO requests(url,user)
                          VALUES(?,?);"""
        cur.execute(sql, (url, username))
        self.conn.commit()

    def get_url_file_id(self, url, quality='min'):
        file_id = self.conn.execute("""SELECT file_id FROM uploaded_files WHERE url=? AND quality=?""",
                                    (url, quality)).fetchone()
        if file_id:
            return file_id[0]
        return None

    def get_chat_quality(self, chat_id):
        quality = self.conn.execute("""SELECT quality FROM settings WHERE chat_id=?""", (chat_id,)).fetchone()
        if quality:
            return quality[0]
        return None

    def set_chat_settings(self, chat_id, quality):
        cur = self.conn.cursor()
        sql = """UPDATE settings
                      SET quality = ?
                      WHERE chat_id = ?"""
        cur.execute(sql, (quality, chat_id))
        self.conn.commit()
