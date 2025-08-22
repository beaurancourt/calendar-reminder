# Calendar Reminder Setup Guide

This application reads your Google Calendar events daily at 8am EST and sends a summary to your Pushover app.

## Prerequisites

- Python 3.7 or higher
- A Google account with calendar access
- A Pushover account

## Installation Steps

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Set up Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"
4. Configure OAuth consent screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (or "Internal" if you have Google Workspace)
   - Fill in required fields (app name, support email, developer email)
   - Click "Save and Continue"
   - Skip scopes section (click "Save and Continue")
   - In "Test users" section, click "+ Add Users"
   - Add your Gmail address
   - Click "Save and Continue" then "Back to Dashboard"
5. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Give it a name (e.g., "Calendar Reminder")
   - Download the credentials
6. Save the downloaded file as `credentials.json` in the project root directory

### 3. Set up Pushover

1. Sign up for a [Pushover account](https://pushover.net/)
2. After logging in, note your User Key from the main dashboard
3. Create a new application:
   - Go to "Your Applications" at the bottom of the page
   - Click "Create an Application/API Token"
   - Fill in the details (name, description, etc.)
   - Note the API Token/Key that's generated

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   PUSHOVER_USER_KEY=your_pushover_user_key
   PUSHOVER_API_TOKEN=your_pushover_api_token
   ```

3. Optional configurations in `.env`:
   - `GOOGLE_CALENDAR_ID`: Use "primary" for your main calendar, or specify a calendar ID
   - `SUMMARY_TIME`: Set the time for daily summary (24-hour format, default: 08:00)
   - `TIMEZONE`: Your timezone (default: America/New_York for EST)

### 5. Authorize Google Calendar Access

On first run, you'll need to authorize the application:

```bash
python main.py test
```

This will:
- Open a browser window for Google authentication
- Ask you to authorize calendar access
- Save the authentication token locally

## Running the Application

### Test Mode

To test the summary generation immediately:

```bash
python main.py test
```

### Continuous Mode

To run the scheduler that sends daily summaries:

```bash
python main.py
```

The application will:
- Run continuously in the foreground
- Send a calendar summary every day at the configured time (default 8am EST)
- Display status messages in the console

### Running as a Background Service

#### On Linux/macOS using nohup:

```bash
nohup python main.py > calendar-reminder.log 2>&1 &
```

#### On Linux using systemd:

1. Create a service file `/etc/systemd/system/calendar-reminder.service`:

```ini
[Unit]
Description=Calendar Reminder Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/calendar-reminder
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/calendar-reminder/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:

```bash
sudo systemctl enable calendar-reminder
sudo systemctl start calendar-reminder
```

#### On macOS using launchd:

1. Create a plist file `~/Library/LaunchAgents/com.user.calendar-reminder.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.calendar-reminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/calendar-reminder/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/calendar-reminder</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/calendar-reminder.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/calendar-reminder.error.log</string>
</dict>
</plist>
```

2. Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.user.calendar-reminder.plist
```

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:
1. Delete `token.json` if it exists
2. Run `python main.py test` to re-authenticate

### Time Zone Issues

Make sure your `TIMEZONE` in `.env` matches your actual timezone. You can find timezone names [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

### Pushover Not Receiving Messages

1. Verify your User Key and API Token are correct
2. Check that your Pushover app is installed and logged in on your device
3. Test Pushover independently using their web interface

## Security Notes

- Keep your `.env` file private and never commit it to version control
- The `credentials.json` and `token.json` files contain sensitive data - keep them secure
- Consider restricting file permissions:
  ```bash
  chmod 600 .env credentials.json token.json
  ```
