FROM python:3.11.4-slim-buster
# Set the working directory
WORKDIR /app  

# Copy your application code into the container

COPY requirements.txt /app/requirements.txt

RUN pip cache purge
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .