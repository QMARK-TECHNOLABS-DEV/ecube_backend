FROM python:3.11.4-slim-buster
# Set the working directory
RUN pip install django
COPY . .
RUN python manage.py migrate

CMD ["python","manage.py","runserver","0.0.0.0.8002"]