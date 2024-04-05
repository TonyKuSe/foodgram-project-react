from enum import Enum, IntEnum


class Tuples(tuple, Enum):
    # Размер сохраняемого изображения рецепта
    RECIPE_IMAGE_SIZE = 500, 500
    # Поиск объектов только с переданным параметром.
    # Например только в избранном: `is_favorited=1`
    SYMBOL_TRUE_SEARCH = '1', 'true'
    # Поиск объектов не содержащих переданный параметр.
    # Например только не избранное: `is_favorited=0`
    SYMBOL_FALSE_SEARCH = '0', 'false'


class Limits(IntEnum):
    DEF_NUM = 0
    DEF_MIN_LEN = 1
    MAX_LEN_EMAIL = 256
    MAX_LEN_USERNAME = 150
    MAX_LEN_FIRST_NAME = 150
    MAX_LEN_LAST_NAME = 150
    MAX_LEN_NAME = 200
    MAX_LEN_TEXTFIELD = 2000
    MIN_COOKING_TIME = 0
    MAX_COOKING_TIME = 32000
    MAX_LEN_CHARFIELD_ING = 200
    MAX_LEN_CHARFIELD = 200
    DEF_MAX_LEN = 7
    MAX_MEASUREMENT_UNIT = 20
    MIN_AMOUNT_INGREDIENTS = 1
    MAX_AMOUNT_INGREDIENTS = 32000


class UrlQueries(str, Enum):
    # Параметр для поиска ингридиентов по вхождению значения в название
    SEARCH_ING_NAME = 'name'
    # Параметр для поиска объектов в списке "избранное"
    FAVORITE = 'is_favorited'
    # Параметр для поиска объектов в списке "покупки"
    SHOP_CART = 'is_in_shopping_cart'
    # Параметр для поиска объектов по автору
    AUTHOR = 'author'
    # Параметр для поиска объектов по тэгам
    TAGS = 'tags'
