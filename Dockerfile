FROM python:3.7

WORKDIR /fastapi

ADD requirements.txt /fastapi/requirements.txt
RUN pip install -r /fastapi/requirements.txt

COPY ./api /fastapi/api
COPY ./lib /fastapi/lib
COPY ./client/dist /fastapi/client/dist
COPY ./rq-workers /usr/src/workers

ENV PYTHONPATH="/fastapi:${PYTHONPATH}"
