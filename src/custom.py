from telebot import types
from enum import Enum

class Texts(Enum):
    CANCEL = 'Отменить❌'
    SAVE = 'Сохранить✔️'
    SKIP = 'Далее'
    MALE = 'Парень'
    FEMALE = 'Девушка'
    NO_SEX = 'Не указывать'
    AGE = 'Возраст'
    SEX = 'Пол'
    NAME = 'Имя'
    DESCRIPTION = 'Описание'
    PHOTOS = 'Фотографии'
    DELETE = 'Удалить🗑️'
    SEARCH = 'Смотреть анкеты'
    EDIT = 'Редактировать анкету'
    CREATE = 'Заполнить анкету заново'
    CONFIRM = 'Готово'
    PHOTOS_AGAIN = 'Заполнить фотографии заново'
    ADD_PHOTO = 'Добавить➕'

class Buttons(Enum):
    CANCEL = types.KeyboardButton(Texts.CANCEL.value)
    SAVE = types.KeyboardButton(Texts.SAVE.value)
    SKIP = types.KeyboardButton(Texts.SKIP.value)
    MALE = types.KeyboardButton(Texts.MALE.value)
    FEMALE = types.KeyboardButton(Texts.FEMALE.value)
    NO_SEX = types.KeyboardButton(Texts.NO_SEX.value)
    AGE = types.KeyboardButton(Texts.AGE.value)
    SEX = types.KeyboardButton(Texts.SEX.value)
    NAME = types.KeyboardButton(Texts.NAME.value)
    DESCRIPTION = types.KeyboardButton(Texts.DESCRIPTION.value)
    PHOTOS = types.KeyboardButton(Texts.PHOTOS.value)
    DELETE = types.KeyboardButton(Texts.DELETE.value)
    SEARCH = types.KeyboardButton(Texts.SEARCH.value)
    EDIT = types.KeyboardButton(Texts.EDIT.value)
    CREATE = types.KeyboardButton(Texts.CREATE.value)
    CONFIRM = types.KeyboardButton(Texts.CONFIRM.value)
    PHOTOS_AGAIN = types.KeyboardButton(Texts.PHOTOS_AGAIN.value)
    ADD_PHOTO = types.KeyboardButton(Texts.ADD_PHOTO.value)

class Markups(Enum):
    @staticmethod
    def create_markup( buttons : list, on_rows : list = None):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        if not on_rows:
            on_rows = [len(buttons)]
        start = 0
        for buttons_on_row in on_rows:
            buttons_to_add = []
            for i in range(start, start + buttons_on_row):
                buttons_to_add.append(buttons[i].value)
            markup.row(*buttons_to_add)
            start += i + 1
        return markup
    
    CANCEL = create_markup([Buttons.CANCEL])
    MAIN_MENU = create_markup([Buttons.SEARCH, Buttons.EDIT, Buttons.CREATE])
    DEFAULT = create_markup([Buttons.SKIP, Buttons.CANCEL])
    EDIT_MENU = create_markup([Buttons.AGE, Buttons.SEX, Buttons.NAME, Buttons.DESCRIPTION, Buttons.PHOTOS, Buttons.SAVE, Buttons.CANCEL], [5, 2])
    SEX = create_markup([Buttons.MALE, Buttons.FEMALE, Buttons.NO_SEX, Buttons.CANCEL], [3, 1])
    PHOTO_EDIT = create_markup([Buttons.DELETE, Buttons.CANCEL])
    SAVE = create_markup([Buttons.SAVE, Buttons.CANCEL])
