FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY diff_service.py .
COPY nf_profile_schema.json .
COPY comparison_rules.yaml .
EXPOSE 9100
CMD ["python", "diff_service.py"]