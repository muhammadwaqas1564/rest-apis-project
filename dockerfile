FROM python:3.11.1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["gunicorn" , "--bind", "0.0.0.0:80","app:craete_app()"]
