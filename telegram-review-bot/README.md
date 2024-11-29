# Telegram Review Bot

A Python Telegram bot that processes archive files, extracts project structures, parses `<REVIEW></REVIEW>` tags in code comments, and generates diffs with placeholder replacements.

## Features

- **Archive Support:** Accepts RAR, ZIP, and 7z archive formats.
- **Project Structure:** Extracts and sends back the project directory structure.
- **Review Tag Parsing:** Searches for `<REVIEW></REVIEW>` tags within comments and generates diffs for the subsequent lines.
- **Diff Generation:** Outputs diffs with placeholders for the replacement lines.

## Setup

### Prerequisites

- **Python 3.8+**
- **Poetry** for dependency management. Install from [Poetry's official site](https://python-poetry.org/docs/#installation).
- **System Dependencies for Patool**:
  - For RAR extraction, ensure that `unrar` is installed on your system.
    - **Ubuntu:** `sudo apt-get install unrar`
    - **macOS (with Homebrew):** `brew install unrar`
    - **Windows:** Download from [Rarlab](https://www.rarlab.com/rar_add.htm) and make sure it's in your PATH.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/telegram_review_bot.git
   cd telegram_review_bot
   ```

2. **Install Dependencies**

   ```bash
   poetry install
   ```

3. **Configure the Bot**

   - Rename the `.env.example` to `.env` and add your Telegram bot token.

     ```bash
     cp .env.example .env
     ```

   - Open `.env` and add your bot token:

     ```
     BOT_TOKEN=your_telegram_bot_token_here
     ```

4. **Run the Bot**

   ```bash
   poetry run telegram-review-bot
   ```

   The bot will start polling for messages.

## Usage

1. **Start the Bot**

   Open Telegram and search for your bot. Start a conversation by sending `/start`.

2. **Send an Archive**

   Send an archive file (RAR, ZIP, 7z) to the bot.

3. **Receive Outputs**

   - **Project Structure:** The bot will reply with the directory structure of the extracted project.
   - **Review Diffs:** If `<REVIEW></REVIEW>` tags are found, it will send diffs showing the original line and a placeholder for the replacement.

## Example

1. **User:** `/start`

   **Bot:** `Hello! Send me an archive file (RAR, ZIP, 7z) and I will process it.`

2. **User:** _Sends `project.zip` containing:_

   ```
   project/
   ├── main.py
   └── utils.py
   ```

   - `main.py` contains:

     ```python
     # <REVIEW></REVIEW>
     print("Hello, World!")
     ```

   - `utils.py` contains no review tags.

3. **Bot:**

   ```
   📂 *Project Structure:*
   ```

   project/
   main.py
   utils.py

   ```

   📝 *Review Diffs:*
   ```

   **File:** `project/main.py`

   - `print("Hello, World!")`

   * `<<<REPLACEMENT LINE>>>`

   ```

   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT](LICENSE)
