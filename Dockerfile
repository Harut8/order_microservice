FROM python:latest

WORKDIR /order_microservice

COPY . .

RUN pip install -r requirements.txt

RUN pip install pydantic[email]

EXPOSE 8000

CMD ["python", "main.py"]