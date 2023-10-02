FROM python:3.11.4-slim-buster

RUN pip install --upgrade setuptools
# Install PostgreSQL development files
RUN apt-get update && apt-get install -y libpq-dev &&  apt-get install python3-psycopg2 -y

# Set the working directory
WORKDIR /ecube_backend

# Copy your application code into the container
COPY requirements.txt /app/requirements.txt
RUN pip cache purge
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# copy project
COPY . .