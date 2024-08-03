from telebot.handler_backends import State, StatesGroup

class Form:
    def __init__(self, id=0, name=None, age=None, sex=None, desc=None, photos=[]):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.desc = desc
        self.photos = photos

    def get_data(self):
        return (self.id, self.name, self.age, self.sex, self.desc, self.photos)
    
    def set_data(self, data):
        self.id, self.name, self.age, self.sex, self.desc, self.photos = data

    def show_data(self):
        text = f'''{self.name}, {self.age} лет.\nПол: {self.sex} \n\nОбо мне:\n{self.desc}'''
        return text
    
class FormState(StatesGroup):
    main_menu = State()
    name = State()
    age = State()
    sex = State()
    desc = State()
    photos = State()
    save = State()
    edit_menu = State()
    edit_name = State()
    edit_age = State()
    edit_sex = State()
    edit_desc = State()
    edit_save = State()
    edit_photos = State()
    edit_numbered_photo = State()
