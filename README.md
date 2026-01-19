# Webb Austin Tech Events - Weekly Email Automation

Automatically receive a beautiful HTML email every Sunday with upcoming tech events from Webb Austin.

## Features

- **Automated Weekly Emails**: Get event updates every Sunday at 9:00 AM
- **Beautiful HTML Formatting**: Clean, professional email design with event cards
- **Smart Web Scraping**: Flexible scraper that adapts to different website structures
- **Easy Configuration**: Simple JSON config file
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Multiple Scheduling Options**: Python-based scheduler or cron job
- **Comprehensive Logging**: Track all operations and debug issues easily

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gmail

You need a Gmail account and an App Password:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification (enable if not already)
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password (no spaces)

### 3. Update Configuration

Edit `config.json`:

```json
{
  "webb_url": "https://webbatx.com/",
  "sender_email": "your_email@gmail.com",
  "sender_password": "your_16_char_app_password",
  "recipient_email": "your_email@gmail.com"
}
```

### 4. Test the System

```bash
python3 test_system.py
```

This will:
- Verify your configuration
- Test web scraping
- Generate a sample email
- Optionally send a test email

### 5. Start the Scheduler

**Option A: Python Scheduler (Recommended)**

```bash
python3 scheduler.py
```

This keeps running in the background. To run it permanently:

```bash
# Linux/Mac with nohup
nohup python3 scheduler.py &

# Or use screen/tmux
screen -S webb-emailer
python3 scheduler.py
# Press Ctrl+A then D to detach
```

**Option B: Cron Job (Linux/Mac)**

```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

## File Structure

```
Webb-Austin-Events-Sunday-Email/
├── webb_events_emailer.py   # Main scraper and emailer
├── scheduler.py              # Weekly scheduler
├── config.json               # Your email configuration
├── requirements.txt          # Python dependencies
├── test_system.py            # System testing script
├── setup_scheduler.sh        # Cron setup script
├── README.md                 # This file
├── QUICKSTART.txt            # Quick reference guide
├── webb_emailer.log          # Application logs
└── scheduler.log             # Scheduler logs
```

## How It Works

### Web Scraping

The scraper uses multiple strategies to find events on Webb's website:

1. **Primary Strategy**: Looks for common event container patterns
2. **Fallback Strategy**: Searches for event-related links and nearby content
3. **Flexible Selectors**: Automatically adapts to different HTML structures

### Email Format

Each email includes:
- Header with gradient background and current date
- Individual cards for each event with:
  - Event title
  - Date and time
  - Description (if available)
  - Direct link button
- Professional footer with source link

### Scheduling

Two options available:

1. **Python Scheduler**: Uses the `schedule` library, runs continuously
2. **Cron Job**: System-level scheduling (Linux/Mac only)

## Customization

### Change Email Schedule

Edit `scheduler.py` line 28:

```python
# Every Sunday at 9:00 AM (current)
schedule.every().sunday.at("09:00").do(job)

# Every Monday at 8:00 AM
schedule.every().monday.at("08:00").do(job)

# Every day at 7:00 AM
schedule.every().day.at("07:00").do(job)
```

### Customize Email Styling

Edit the `create_html_email()` method in `webb_events_emailer.py` to change:
- Colors (line 145-165)
- Fonts
- Layout
- Header/footer content

### Update Scraping Selectors

If Webb changes their website structure, update the `event_selectors` array in `webb_events_emailer.py` (line 54):

```python
event_selectors = [
    {
        'container': 'div.your-event-class',
        'title': 'h3.event-title',
        'date': '.event-date',
        'desc': '.event-description',
        'link': 'a'
    }
]
```

## Troubleshooting

### No Events Found

1. Check if Webb's website is accessible: visit https://webbatx.com/
2. Review logs in `webb_emailer.log`
3. The website structure may have changed - update selectors
4. Run with verbose logging to see what's being scraped

### Email Not Sending

1. Verify Gmail credentials in `config.json`
2. Ensure you're using an App Password, not your regular password
3. Check 2-Step Verification is enabled on your Google account
4. Review `webb_emailer.log` for specific error messages
5. Test with: `python3 test_system.py`

### Scheduler Not Running

1. Check if process is running: `ps aux | grep scheduler.py`
2. Review `scheduler.log` for errors
3. Ensure system time is correct: `date`
4. For cron jobs, check cron logs: `grep CRON /var/log/syslog`

### 403 Forbidden Error

The website is blocking the request. Try:
1. Updating the User-Agent header in `webb_events_emailer.py`
2. Adding delays between requests
3. Checking if the website has rate limiting

## Advanced Usage

### Run One-Time Email

```bash
python3 webb_events_emailer.py
```

### Change Recipient

You can send emails to different addresses by updating `recipient_email` in `config.json`.

### Multiple Recipients

Edit `send_email()` method in `webb_events_emailer.py`:

```python
msg['To'] = ', '.join(['email1@gmail.com', 'email2@gmail.com'])
```

### Save Events to File

Add this to the `run()` method:

```python
import json
with open('events.json', 'w') as f:
    json.dump(events, f, indent=2)
```

## Security Notes

- **Never commit `config.json` with real credentials to version control**
- Use App Passwords, not your main Gmail password
- Keep your App Password secure
- The `.gitignore` file should include `config.json`

## Dependencies

- `requests`: HTTP library for web scraping
- `beautifulsoup4`: HTML parsing and scraping
- `schedule`: Task scheduling
- `lxml`: Fast HTML parser for BeautifulSoup

## Support

If you encounter issues:

1. Check the logs (`webb_emailer.log`, `scheduler.log`)
2. Run the test script: `python3 test_system.py`
3. Verify your configuration is correct
4. Ensure all dependencies are installed

## License

This is a personal automation tool. Feel free to modify and use as needed.

## Future Enhancements

Potential improvements you could add:

- Email digest of multiple event sources
- Event filtering by category/topic
- Calendar file (.ics) attachments
- SMS notifications
- Slack/Discord integration
- Web dashboard to view events

---

**Created with ❤️ for the Austin tech community**
