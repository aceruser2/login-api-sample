第一次 
    alembic init alembic
    alembic revision --autogenerate -m "first migration" 
    alembic upgrade head
第二次 
    alembic upgrade head && uvicorn server:app --host 0.0.0.0 --port 8000 --reload
     """ http://0.0.0.0:8000/docs


    jwt
    https://pyjwt.readthedocs.io/en/latest/algorithms.html


    wait
    1. 去識別
    2. 異步
    3. 權限管理(不實做)
    
    同步套件
    pip install psycopg2-binary
    dbconn="postgresql+psycopg2://user:123456@localhost:7000/db"
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE EXTENSION pgcrypto;

    sudo service docker start