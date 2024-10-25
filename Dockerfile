FROM python:3.12-slim-buster as base
RUN mkdir /app
COPY requirements.txt /app/

WORKDIR /app

RUN apt-get -y update && apt-get install -y --no-install-recommends build-essential gcc g++ libsasl2-dev python-dev

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


FROM python:3.12-slim-buster
ENV TZ=$TZ
RUN date
RUN apt-get -y update && apt-get -y upgrade
RUN groupadd -g 1000 docker && \
    useradd -r -u 1000 -g docker docker

RUN mkdir /app && chown docker:docker /app
# 為了讓/app 的擁有者為python
WORKDIR /app



COPY --chown=docker:docker --from=base /app/venv /app/venv
COPY --chown=docker:docker . /app




EXPOSE 8000
USER docker
ENV PATH="/app/venv/bin:$PATH"
# CMD python server.py