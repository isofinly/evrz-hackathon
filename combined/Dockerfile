FROM python:3.12-slim

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

RUN pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

CMD ["poetry", "run", "telegram_review_bot"]
