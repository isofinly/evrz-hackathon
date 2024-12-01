# Telegram Review Bot

A Python Telegram bot that processes archive files, extracts project structures, parses code, and generates review report based on the provided knowledge base.

## Features

- **File Support:** Accepts various file formats.
- **Archive Support:** Accepts RAR, ZIP, and 7z archive formats.
- **Review Preview:** Sends paginated preview of the review results.
- **Review Download:** Provides a button to download the full review report as a PDF file.
- **RAG:** Uses RAG to provide context for the model.
- **Small LLM:** Uses Mistral-nemo 12B model for delivering comprehensive review requiring less than 20GB of VRAM.

## Setup

### Prerequisites

- **Python 3.11+**
- **Poetry** for dependency management. Install from [Poetry's official site](https://python-poetry.org/docs/#installation)
- **MinIO Server** with DNS record for pre-assigned URLs (credentials will be provided separately)
- **System Dependencies**:
  - For RAR extraction, ensure that `unrar` is installed on your system:
    - **Ubuntu:** `sudo apt-get install unrar`
    - **macOS (with Homebrew):** `brew install unrar`
    - **Windows:** Is not supported due to the lack of supported libraries.

### Important Note for Local Development

If running the bot locally (outside Docker), you'll need to handle PyTorch installation separately:

- Either run: `pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu`
- Or uncomment the `torch` dependency in `pyproject.toml` and try to install it, but it **may fail**.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/isofinly/telegram_review_bot.git
   cd telegram_review_bot
   ```

2. **Configure Environment Variables**
   Create a `.env` file with the following required variables:

   ```
   BOT_TOKEN=your_telegram_bot_token
   MINIO_ENDPOINT=your_minio_endpoint
   MINIO_ACCESS_KEY=your_minio_access_key
   MINIO_SECRET_KEY=your_minio_secret_key
   MINIO_SECURE=true_or_false
   MODEL_API_KEY=your_model_api_key
   ```

   Note: MinIO credentials will be provided via manager and cloud drive document.

3. **Choose Your Installation Method**

   **Docker (Recommended)**:

   ```bash
   docker-compose up -d
   ```

   This will start both the bot and MinIO server containers.

   **Local Installation**:

   ```bash
   poetry install
   poetry run telegram-review-bot
   ```

## Usage

1. **Start the Bot**

   Open Telegram and search for your bot. Start a conversation by sending `/start`.

2. 2.1 **Send a File**

   Send a file to the bot.

   2.2 **Send an Archive**

   Or you can send an archive file (RAR, ZIP, 7z) to the bot.

3. **Receive Outputs**

   - **Review Preview:** The bot will reply with paginated preview of the review results.
   - **Review Download:** Use the provided button to download the full review report as a PDF file.

## Packages structure

- `src/bot` — Telegram bot code.
- `src/review` — Code review logic.
- - `src/review/parsers` - Code chunking logic

## Review pipeline

1. **RAG**: Create a vector database from the knowledge base to align code chunks with relevant review examples.
2. **Review**:
   - Parse project structure
   - Analyze the structure of individual files.
   - Divide files into manageable chunks.
   - Use RAG to generate prompts and contextual information for the model.
   - Generate and format the review


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT](LICENSE)
