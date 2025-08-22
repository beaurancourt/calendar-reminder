# Calendar Reminder

A self-hosted Python application that sends daily Google Calendar summaries to your phone via Pushover.

## Features

- 📅 Reads events from your Google Calendar
- ⏰ Sends daily summaries at 8am EST (configurable)
- 📱 Delivers notifications via Pushover
- 🔒 Secure OAuth2 authentication
- 🏠 Self-hosted - your data stays private

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Google Calendar API credentials
4. Configure Pushover credentials
5. Run: `python main.py`

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Usage

### Test the summary immediately:
```bash
python main.py test
```

### Run the daily scheduler:
```bash
python main.py
```

## Configuration

Edit `.env` file to customize:
- `SUMMARY_TIME`: Time for daily summary (default: 08:00)
- `TIMEZONE`: Your timezone (default: America/New_York)
- `GOOGLE_CALENDAR_ID`: Calendar to read (default: primary)

## Requirements

- Python 3.7+
- Google account with calendar
- Pushover account
