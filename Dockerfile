FROM python:3.10.13
#-alpine3.17

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","app.py"]

## Build the Docker Image
## docker build -t my-python-app .

## Run the Docker Container
