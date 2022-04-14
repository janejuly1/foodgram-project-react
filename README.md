![build status](https://github.com/janejuly1/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# Foodgram
Сборник вкусных рецептов для любого повода

# Где посмотреть
http://178.154.220.70/redoc/

# API для Foodgram
### Технологии
Python 3.7
Django 2.2.19
##### ✨ Проект Foodgram
- Проект Foodgram собирает рецепты (Recipe) из всевозможных ингридиентов (Ingredient). 
- Рецепты разбиты по тегам (Tag). При создании рецепта можно добавить несколько тегов из предустановленных, например: «Завтрак», «Обед», «Ужин». Новые теги может создавать только администратор.
- Любой понравившейся рецепт можно добавить в избранное(Favourites).
- Если человек хочет приготовить несколько блюд, то добавив рецепты в список покупок(Shopping Cart), сможет скачать полный перечень необходимых ингридиентов и их общее количество. 
- Любой авторизованный пользователь может подписаться на понравившегося автора, чтобы не пропустить его новые рецепты.
#### Как поднять контейнер:

- Поднять контейнер из директории infra
```
docker-compose up
```
- В контейнере django нужно выполнить миграции, создать суперпользователя и собрать статику. 
```
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
docker-compose exec django python manage.py collectstatic --no-input
```
- Остановить контейнеры
```
docker-compose down
```
#### Шаблон наполнения env-файла
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12356789
DB_HOST=db
DB_PORT=5432
```
#### Наполнение базы данными

- Вы можете наполнить базу вручную, используя функционал сайта, или через панель администратора. А можете перенести данные из локального проекта 
- Для этого копируйте файл dump.json с локального компьютера на сервер.
- Зайдите в директорию с файлом manage.py, экспортируйте данные в файл.
```
python manage.py dumpdata > dump.json
```
- Скопируйте файл dump.json с локального компьютера на сервер. 
```
scp dump.json username@host:/home/имя_пользователя/.../папка_проекта_с_manage.py/ 
```

- Чтобы сделать резервное копирование базы данных:
```
sudo -u postgres pg_dump <name> > <new_name>.dump
```

- Чтобы восстановить данные, нужно создать пустую базу данных (назывите её как-то иначе, нежели основную) и загрузить в неё данные из резервной копии. 
```
sudo -u postgres psql -c 'create database foodgram2;' # Создали пустую базу данных с именем foodgram2
sudo -u postgres psql -d foodgram2 -f foodgram_backup.dump # Загрузили в неё данные из дампа 
```
- ✨Magic ✨

# Author
Eugenia Drobova <janejuly1@gmail.com>
