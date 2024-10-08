FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt /app/
RUN apt-get -y update && apt-get install -y libzbar-dev
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt


COPY . /app

EXPOSE 8000

# CMD alembic upgrade head && uvicorn --host 0.0.0.0 --port 8000 server:app --reload --proxy-headers