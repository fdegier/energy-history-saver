FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY data data
RUN touch data/energy.db
RUN python data/create_tables.py

COPY main.py .

CMD python main.py -w 4
