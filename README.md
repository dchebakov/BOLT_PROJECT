# [bmstu.fun](http://bmstu.fun)

Это сайт-помощник для студентов технических специальностей. Здесь представлена масса задач по различным дисциплинам.
* Выберите нужный раздел, найдите интересующую вас задачу (или воспользуйтесь поиском по сайту)
* Введите свои исходные данные
* Наслаждайтесь подробным решением именно вашей задачи!

## Запуск локальной версии проекта

#### 1. Склонировать репозиторий
```
$ git clone https://github.com/dchebakov/bmstu-fun
```

#### 2. Создать и запустить виртуальное окружение
```
$ python -m venv venv
$ source venv/bin/activate
```

#### 3. Установить зависимости
```
$ pip install -r requirements.txt
```

#### 4. Создать базу данных
Зайти в консоль postgres:
```
$ sudo -u postgres psql
```

И выполнить следующие команды:
```postgresql
create user admin with password 'qwerty';
create database bmstu_fun owner admin;
```

#### 5. Заполнить базу данных
```
$ cd fixtures
$ unzip dump.zip
$ cd ..
$ sudo -u postgres psql bmstu_fun < fixtures/dump.pgsql
$ mkdir media
```

#### 6. Запустить проект
```
$ python src/manage.py runserver
```
