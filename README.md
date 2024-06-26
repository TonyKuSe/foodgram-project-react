
# Продуктовый помощник Foodgram: 
Foodgram - приложение, которое позволяет пользователям делиться рецептами блюд, подписываться на других авторов и сохранять понравившиеся рецепты в избранное. Также в приложении предусмотрен сервис "Список покупок", с помощью которого пользователь может составлять список продуктов для приготовления выбранных блюд согласно рецептам.

Для запуска проекта Foodgram необходимо выполнить следующие шаги:

1. Установить необходимые компоненты на сервере ВМ Yandex.Cloud, использовать Docker и docker-compose.
2. Создать папку /infra в домашней директории на сервере.
3. Загрузить актуальные данные на DockerHub из папок /backend и /frontend на локальном компьютере.
4. Перенести файлы docker-compose.yml и default.conf на сервер из папки /infra в текущем репозитории на локальном компьютере.
5. Создать файл .env в директории /infra на сервере и заполнить его настройками для работы с базой данных PostgreSQL.
6. Выполнить команду docker-compose up -d --build в папке /infra на сервере для запуска проекта.

Для завершения настройки на сервере можно выполнить следующие действия:

- Остановить проект: docker-compose stop

- Удалить проект вместе с данными: docker-compose down -v

- Выполнить необходимые команды для бекенда: python manage.py makemigrations, python manage.py migrate --noinput, python manage.py createsuperuser, python manage.py collectstatic --no-input, python manage.py load_tags, python manage.py load_ingrs.

После выполнения этих шагов приложение Foodgram будет успешно запущено на сервере и будет доступно по указанному адресу или IP. Также доступна документация к API после запуска проекта.

https://food-contact.online/
### Документация к API доступна после запуска

```url
http://127.0.0.1/api/docs/
```