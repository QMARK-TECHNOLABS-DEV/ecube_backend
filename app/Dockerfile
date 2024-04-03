FROM python:3.11.4-slim-buster

RUN pip install --upgrade setuptools

RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libpq-dev && apt-get install -y python3-dev && apt-get install -y gcc && apt-get install -y libglib2.0-0 
# set work directory
WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# copy project
COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]