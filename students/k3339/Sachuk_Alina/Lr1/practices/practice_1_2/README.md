# Практика 1.2

Результат практики находится в итоговом приложении ЛР1:

- подключение PostgreSQL и выдача сессии — `app/database.py`;
- SQLModel-таблицы и связи — `app/models.py`;
- CRUD — `app/routers/`;
- вложенное отображение авторов, владельцев и книг — `app/presenters.py`;
- many-to-many с дополнительными полями `role` и `position` — модель
  `BookAuthorLink`.

Применение схемы выполняется миграцией `migrations/versions/0001_initial_schema.py`.
