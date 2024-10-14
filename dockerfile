FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090", "--workers", "9"]
