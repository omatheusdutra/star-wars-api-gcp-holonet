FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

CMD ["uvicorn", "holonet.main:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]
