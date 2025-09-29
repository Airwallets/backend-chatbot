FROM python:3.12

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY *.csv /app/
COPY startup.py /app/startup.py
CMD ["bash", "-c",  "python startup.py"]
