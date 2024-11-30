FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    g++ \
    gcc \
    make \
    p7zip-full \
    unrar-free \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy the entire telegram-review-bot directory
COPY . .

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Run the bot
CMD ["poetry", "run", "telegram_review_bot"]
