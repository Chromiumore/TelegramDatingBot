import sqlite3
from form import Form

class Database:
    def __init__(self, file):
        self.file = file
        self.connection = sqlite3.connect(self.file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS forms (
                        id   INTEGER PRIMARY KEY
                        UNIQUE
                        NOT NULL,
                        name TEXT,
                        age  INTEGER,
                        sex  TEXT,
                        desc TEXT
                        );'''
        )

        self.cursor.execute('''
                       CREATE TABLE IF NOT EXISTS photos (
                       photo_id TEXT    PRIMARY KEY
                       UNIQUE
                       NOT NULL,
                       user_id  INTEGER REFERENCES forms (id) 
                       NOT NULL
                       );''')

        self.connection.commit()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def upload_form(self, form : Form):
        id = form.id
        name = form.name
        age = form.age
        sex = form.sex
        desc = form.desc
        photos = form.photos
        self.cursor.execute(f'''
                       DELETE FROM forms WHERE id = {id};
                       ''')
        self.cursor.execute(f'''
                       DELETE FROM photos WHERE user_id = {id};
                       ''')
        self.cursor.execute(f'''
                       INSERT INTO forms (id, name, age, sex, desc)
                       VALUES({id}, '{name}', {age}, '{sex}', '{desc}');
                       ''')
        for i in range(len(photos)):
            self.cursor.execute(f'''
                           INSERT INTO photos (photo_id, user_id)
                           VALUES('{photos[i]}', '{id}');
                           ''')
        self.connection.commit()
            
    def download_data(self, id : int):
        self.cursor.execute(f'''
                       SELECT * FROM forms
                       WHERE id = {id}
                       ''')
        res = self.cursor.fetchone()
        self.connection.commit()
        return res
    
    def download_photos(self, id : int):
        self.cursor.execute(f'''
                       SELECT photo_id FROM photos
                       WHERE user_id = {id}
                       ''')
        req = self.cursor.fetchall()
        photos = [x[0] for x in req]
        return photos

    def check_field_exists(self, id):
        select = self.download_data(id)
        return not select is None
    
    def download_form(self, id):
        data = list(self.download_data(id))
        photos = list(self.download_photos(id))
        data.append(photos)
        form = Form(*data)
        return form
