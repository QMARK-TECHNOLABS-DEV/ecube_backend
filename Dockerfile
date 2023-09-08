FROM python:3.11.4
WORKDIR /app
COPY ../ecube_backend /app/

RUN pip install --upgrade pip --no-cache-dir

RUN pip install -r /app/requirements.txt --no-cache-dir

CMD [ "python3" , "manage.py" , "runserver" , "0.0.0.0:8000" ]