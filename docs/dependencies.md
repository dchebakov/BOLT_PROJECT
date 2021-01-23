### Обновление python зависимостей

Чтобы обновить разом все зависимости можно воспользоваться следующей командой (подробнее см. [stackoverflow](https://stackoverflow.com/questions/2720014/how-to-upgrade-all-python-packages-with-pip)):
```bash
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
pip freeze > requirements.txt
```

### Последняя доступная версия

Для просмотра версий определённого пакета существует пакет [`yolk3k`](https://pypi.org/project/yolk3k/).

К примеру, последняя версия Django:
```bash
yolk -V django
```

Просмотр установленных пакетов:
```bash
yolk -l
```
