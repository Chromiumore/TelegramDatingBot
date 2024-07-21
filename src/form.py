class Form:
    def __init__(self, id=0, name=None, age=None, sex=None, desc=None):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.desc = desc

    def get_data(self):
        return (self.id, self.name, self.age, self.sex, self.desc)
    
    def set_data(self, data):
        self.id, self.name, self.age, self.sex, self.desc = data

    def show_data(self):
        text = f'''{self.name}, {self.age} лет.\nПол: {self.sex} \n\nОбо мне:\n{self.desc}'''
        return text
