FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir prometheus_flask_exporter
COPY app.py ./
EXPOSE 7000
CMD ["python", "app.py"]