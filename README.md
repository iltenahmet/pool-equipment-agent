# Pool Equipment Agent
Pool equipment agent is a smart chat assistant that can handle user queries related to pool equipment, store details, and product information.

## Installation
1) To install, open your terminal and navigate to this repository. 

2) Inside this directory create a file names `.env`. You'll need to put your `openai key`, your `bot token` from telegram, and a `google api key` for gathering location information. It should look like this:

```.env
OPENAI_API_KEY=<your-OpenAI-api-key>
BOT_TOKEN=<your-bot-token-from-Telegram>
GOOGLE_API_KEY=<your-google-api-key>
```

3) Once you've set up your `.env` file, create a python virtual environment with the following command.
```bash
# For Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

4) And install the required Python dependencies by running:

```bash
pip install -r requirements.txt
```

5) Once you've installed dependencies, you can start the chatbot by running

```bash
python3 telegram.py
```

6) Once chatbot is running, head over to telegram to chat with the bot.