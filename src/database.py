import sqlite3
from form import Form

class Database:
    def __init__(self, file):
        self.file = file
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        cursor.execute('''
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

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS photos (
                       photo_id TEXT    PRIMARY KEY
                       UNIQUE
                       NOT NULL,
                       user_id  INTEGER REFERENCES forms (id) 
                       NOT NULL
                       );''')

        connection.commit()
        cursor.close()
        connection.close()
        
    def upload_form(self, form : Form):
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        id = form.id
        name = form.name
        age = form.age
        sex = form.sex
        desc = form.desc
        photos = form.photos
        cursor.execute(f'''
                       DELETE FROM forms WHERE id = {id};
                       ''')
        cursor.execute(f'''
                       DELETE FROM photos WHERE user_id = {id};
                       ''')
        cursor.execute(f'''
                       INSERT INTO forms (id, name, age, sex, desc)
                       VALUES({id}, '{name}', {age}, '{sex}', '{desc}');
                       ''')
        for i in range(len(photos)):
            cursor.execute(f'''
                           INSERT INTO photos (photo_id, user_id)
                           VALUES('{photos[i]}', '{id}');
                           ''')
        connection.commit()
        cursor.close()
        connection.close()
            
    def download_data(self, id : int):
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        cursor.execute(f'''
                       SELECT * FROM forms
                       WHERE id = {id}
                       ''')
        res = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return res
    
    def download_photos(self, id : int):
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        cursor.execute(f'''
                       SELECT * FROM photos
                       WHERE user_id = {id}
                       ''')
        photos = cursor.fetchone()
        return photos

    def check_field_exists(self, id):
        select = self.download_data(id)
        return not select is None
    
    def download_form(self, id):
        data = self.download_data(id)
        photos = self.download_photos(id)
        data += photos
        form = Form(*data)
        return form
