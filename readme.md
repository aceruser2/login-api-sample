第一次 
    alembic init alembic
    alembic revision --autogenerate -m "first migration" 
    alembic upgrade head
第二次 
    alembic upgrade head && uvicorn server:app --host 0.0.0.0 --port 8000 --reload
     """ http://0.0.0.0:8000/docs

 postgresql.JSONB(astext_type=sa.Text())
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

    加密 jwt成功

    如果顧客用手機掃描，✅ 用「中介頁面 + JS 發送 POST」最直覺。

    export TESTING=true
    pytest mock_test_api.py