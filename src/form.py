class Form:
    def __init__(self, id=0, name=None, age=None, sex=None, desc=None):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.desc = desc

    def get_data(self):
        return (self.id, self.name, self.age, self.sex, self.desc)

    def show_data(self):
        print(f'id: {self.id}, name: {self.name}, age: {self.age}, sex: {self.sex}')
        print(f'description: {self.desc}')
