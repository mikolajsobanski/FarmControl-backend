FROM  python:3.11.4-alpine


ENV PYTHONUNBUFFERED=1
ENV PYTHONUNBUFFERED 1



WORKDIR /app 
COPY requirements.txt requirements.txt

# install dependencies  
RUN pip3 install -r requirements.txt

# copy from the current directory of the Dockerfile to /api in the image
COPY ./api .

EXPOSE 8080

CMD ["python3","manage.py", "runserver", "0.0.0.0:8080"]