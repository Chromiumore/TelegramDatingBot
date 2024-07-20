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

        connection.commit()
        cursor.close()
        
    def load_form(self, form : Form):
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        id = form.id
        name = form.name
        age = form.age
        sex = form.sex
        desc = form.desc
        cursor.execute(f'''
                       DELETE FROM forms WHERE id = {id};
                       ''')
        cursor.execute(f'''INSERT INTO forms (id, name, age, sex, desc)
                       VALUES({id}, '{name}', {age}, '{sex}', '{desc}');
                       ''')
        connection.commit()
        cursor.close()
            

    def check_field_exists(self, id):
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM forms
                       WHERE id = ''' + str(id))
        res = not cursor.fetchone() is None
        connection.commit()
        cursor.close()
        return res
