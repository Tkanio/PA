FROM python:3.10-slim

WORKDIR /PA

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "nodes.py"]
