## Run Alembic Migrations 

### Configration 

```bash 
cp alembic.ini.example alembic.ini
```

- update the `alembic.ini` with your database credentials ('sqlalchemy.url')

### (Optional) create a new migration 

```bash
amebic revision --autogenerate -m "Add .."
```

### Upgrade the database 

```bash 
alembic upgrade head
```