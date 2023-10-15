# Use the official Python image as a parent image
FROM python:3.11.4-slim-buster

RUN pip install --upgrade setuptools
# Install PostgreSQL development files
RUN apt-get update && apt-get install -y libpq-dev && apt-get install -y python3-dev && apt-get install -y gcc 
# Set the working directory
WORKDIR /app

# Install the python-dotenv library
RUN pip install python-dotenv

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip cache purge
RUN pip install --upgrade pip
# Install any other dependencies
RUN pip install -r requirements.txt

# Command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]