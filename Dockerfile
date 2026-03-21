FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/structured \
    data/chroma_db data/models

EXPOSE 8000 7860

CMD ["python", "-m", "src.api.main"]