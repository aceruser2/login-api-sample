第一次 
    alembic init alembic
    alembic revision --autogenerate -m "first migration" 
    alembic upgrade head
第二次 
    alembic upgrade head && uvicorn server:app --host 0.0.0.0 --port 7002 --reload
     """ http://0.0.0.0:8000/docs


    jwt
    https://pypi.org/project/fastapi-jwt-auth/
    https://pyjwt.readthedocs.io/en/latest/algorithms.html


    wait put auth role
         put user
         get all user,auth,depart,等not filter
         wait add jwt
         