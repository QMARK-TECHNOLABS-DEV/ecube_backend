FROM python:3.11.4-slim-buster

# Install PostgreSQL development files
RUN apt-get update && apt-get install -y libpq-dev

# Set the working directory
WORKDIR /ecube_backend

# Copy your application code into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# copy project
COPY . .