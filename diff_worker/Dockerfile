FROM python:3.10

WORKDIR /diff_worker

COPY diff_worker.py requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "diff_worker.py"]