FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /code

COPY requirements.txt /code

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /code

CMD [ "uvicorn", "main:app" , "--port=5000"]
