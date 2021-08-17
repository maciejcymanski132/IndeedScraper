FROM python:3.7

RUN pip install fastapi uvicorn

WORKDIR /code

COPY requirements.txt /code

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /code

CMD ["python3","app.py"]

