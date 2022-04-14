FROM python:3.7-slim

RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY ./ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
