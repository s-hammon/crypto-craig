FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CMC_PRO_API_KEY=""
ENV DISCORD_TOKEN=""
ENV DB_URL=""
ENV TURSO_AUTH_TOKEN=""
ENV TURSO_AUTH_TOKEN_DISCORD_CLIENT=""

ENTRYPOINT ["python3", "main.py"]
