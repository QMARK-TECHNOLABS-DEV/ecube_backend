FROM python:3.11.4-slim-buster

RUN apt update && apt install nginx -y

COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

COPY . .

RUN pip install -r requirements.txt

WORKDIR /ecube_backend
COPY run.sh .

RUN chmod +x run.sh

CMD ["./run.sh"]