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


`scalar()` 適用於只查詢單一欄位或單一模型（例如 select(User)），且你只需要第一筆資料的第一個欄位（column）的值。常見場景如下：

1. **查詢單一模型的單一物件**  
   例如：`select(User).where(User.id == 1)`  
   用 `db.execute(query).scalar()` 會直接回傳第一個 User 物件。

2. **查詢單一欄位的值**  
   例如：`select(func.count(User.id))`  
   用 `db.execute(query).scalar()` 會回傳 count 結果（整數）。

**不適用於多模型或多欄位 select**  
如果你 select 了多個模型（如 select(User, Role)），scalar 只會回傳第一個欄位（User），而不是 tuple。如果你要 tuple，請用 `.first()` 或 `.one()`。

簡單總結：  
- 只查一個欄位/模型 → 用 `scalar()`  
- 查多個欄位/模型 → 用 `first()`、`one()`、`all()`