FROM python:3.8

COPY . /app
WORKDIR /app/techtrends

RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip install -r requirements.txt
RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]
