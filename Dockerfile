FROM python:3.8-slim-buster

WORKDIR /

COPY requirements.txt requirements.txt
RUN ["pip3", "install", "-r", "requirements.txt"]

COPY . .
# ensure no database in docker environment:
RUN ["rm", "-f", "db.sqlite3"]

CMD ["bash"]

