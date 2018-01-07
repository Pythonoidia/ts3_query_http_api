FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LISTEN_PORT=80

EXPOSE 80

CMD [ "python", "./app.py" ]
