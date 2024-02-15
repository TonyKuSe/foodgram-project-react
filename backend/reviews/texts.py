from .enums import Limits

"""help-texts for users.models"""
USER_HELP_EMAIL = (
    "Обязательно для заполнения. "
    f"Максимум {Limits.MAX_LEN_EMAIL} букв."
)
USER_HELP_USERNAME = (
    "Обязательно для заполнения. "
    f"Максимум {Limits.MAX_LEN_USERNAME} букв."
)

USER_HELP_F_NAME = (
    "Обязательно для заполнения. "
    f"Максимум {Limits.MAX_LEN_FIRST_NAME} букв."
)
USER_HELP_L_NAME = (
    "Обязательно для заполнения. "
    f"Максимум {Limits.MAX_LEN_LAST_NAME} букв."
)
USER_HELP_PASSWORD = (
    "Обязательно для заполнения. "
    f"Максимум {Limits.MAX_LEN_LAST_NAME} букв."
)
