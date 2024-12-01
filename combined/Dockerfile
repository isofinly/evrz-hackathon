FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    g++ \
    gcc \
    make \
    p7zip-full \
    unrar-free \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY . .

RUN pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

RUN poetry config virtualenvs.create false

RUN poetry install

CMD ["poetry", "run", "telegram_review_bot"]
