# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A self-hosted Python application that reads Google Calendar events daily at 8am EST and sends formatted summaries to Pushover for mobile notifications.

## Architecture

- **google_calendar.py**: Handles Google Calendar API authentication and event fetching
- **pushover_client.py**: Manages Pushover API communication
- **summary_generator.py**: Formats calendar events into readable summaries
- **main.py**: Entry point with scheduler and orchestration logic

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test summary generation
python main.py test

# Run scheduler
python main.py
```

## Configuration

Uses `.env` file for configuration:
- Google Calendar API credentials stored in `credentials.json`
- OAuth token cached in `token.json`
- Pushover credentials and settings in `.env`

## Dependencies

- google-api-python-client: Google Calendar API
- python-pushover: Pushover notifications
- schedule: Task scheduling
- pytz: Timezone handling
- python-dotenv: Environment variables