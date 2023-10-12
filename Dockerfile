# Use the official Python image as a parent image
FROM python:3.11.4-slim-buster

# Set the working directory
WORKDIR /app

# Install the python-dotenv library
RUN pip install python-dotenv

# Copy the current directory contents into the container at /app
COPY . /app

# Install any other dependencies
RUN pip install -r requirements.txt

# Command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]