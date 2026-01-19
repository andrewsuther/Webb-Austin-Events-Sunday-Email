#!/usr/bin/env python3
"""
Webb Austin Tech Events Email Scraper
Fetches upcoming tech events from Webb's website and sends a formatted email.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webb_emailer.log'),
        logging.StreamHandler()
    ]
)

class WebbEventsEmailer:
    def __init__(self, config_path='config.json'):
        """Initialize the emailer with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.webb_url = self.config.get('webb_url', 'https://webbatx.com/')
        self.sender_email = self.config['sender_email']
        self.sender_password = self.config['sender_password']
        self.recipient_email = self.config['recipient_email']

    def fetch_events(self):
        """Fetch events from Webb's website."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        try:
            logging.info(f"Fetching events from {self.webb_url}")
            response = requests.get(self.webb_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Strategy 1: Look for common event containers
            # This can be customized based on Webb's actual HTML structure
            event_selectors = [
                {'container': 'div.event-item', 'title': 'h3', 'date': '.event-date', 'desc': '.event-description', 'link': 'a'},
                {'container': 'article.event', 'title': 'h2', 'date': '.date', 'desc': '.description', 'link': 'a'},
                {'container': 'div[class*="event"]', 'title': 'h3, h2, h4', 'date': 'time, .date, [class*="date"]', 'desc': 'p, .desc, [class*="desc"]', 'link': 'a'},
                {'container': 'li[class*="event"]', 'title': 'h3, h2', 'date': 'time, .date', 'desc': 'p', 'link': 'a'},
            ]

            for selector_set in event_selectors:
                event_containers = soup.select(selector_set['container'])
                if event_containers:
                    logging.info(f"Found {len(event_containers)} events using selector: {selector_set['container']}")

                    for container in event_containers:
                        event = self._extract_event_data(container, selector_set)
                        if event and event.get('title'):
                            events.append(event)

                    if events:
                        break  # Found events, stop trying other selectors

            # Fallback: Look for any links with event-related keywords
            if not events:
                logging.info("Using fallback: searching for event-related links")
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    text = link.get_text(strip=True).lower()
                    if any(keyword in text for keyword in ['event', 'meetup', 'conference', 'workshop', 'talk', 'seminar']):
                        event = {
                            'title': link.get_text(strip=True),
                            'url': self._make_absolute_url(link['href']),
                            'date': 'Date TBD',
                            'description': ''
                        }
                        # Try to find nearby date/description
                        parent = link.find_parent(['div', 'article', 'li', 'section'])
                        if parent:
                            date_elem = parent.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower() if x else False)
                            if date_elem:
                                event['date'] = date_elem.get_text(strip=True)
                            desc_elem = parent.find('p')
                            if desc_elem:
                                event['description'] = desc_elem.get_text(strip=True)[:200]

                        events.append(event)

            logging.info(f"Successfully scraped {len(events)} events")
            return events

        except requests.RequestException as e:
            logging.error(f"Error fetching events: {e}")
            return []

    def _extract_event_data(self, container, selectors):
        """Extract event data from a container element."""
        event = {}

        # Extract title
        title_elem = container.select_one(selectors['title'])
        if title_elem:
            event['title'] = title_elem.get_text(strip=True)

        # Extract date
        date_elem = container.select_one(selectors['date'])
        if date_elem:
            event['date'] = date_elem.get_text(strip=True)
        else:
            event['date'] = 'Date TBD'

        # Extract description
        desc_elem = container.select_one(selectors['desc'])
        if desc_elem:
            event['description'] = desc_elem.get_text(strip=True)[:300]
        else:
            event['description'] = ''

        # Extract link
        link_elem = container.select_one(selectors['link'])
        if link_elem and link_elem.get('href'):
            event['url'] = self._make_absolute_url(link_elem['href'])
        else:
            event['url'] = self.webb_url

        return event

    def _make_absolute_url(self, url):
        """Convert relative URLs to absolute URLs."""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.webb_url.rstrip('/')}{url}"
        else:
            return f"{self.webb_url.rstrip('/')}/{url}"

    def create_html_email(self, events):
        """Create a beautiful HTML email from events data."""
        if not events:
            return """
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
                    <h2 style="color: #6b46c1;">Webb Austin Tech Events</h2>
                    <p>No events found this week. Check back next Sunday!</p>
                </div>
            </body>
            </html>
            """

        events_html = ""
        for event in events:
            events_html += f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #2d3748; margin-top: 0; margin-bottom: 10px;">{event['title']}</h3>
                <p style="color: #6b46c1; font-weight: bold; margin: 5px 0;">📅 {event['date']}</p>
                {f'<p style="color: #4a5568; margin: 10px 0; line-height: 1.6;">{event["description"]}</p>' if event.get('description') else ''}
                <a href="{event['url']}" style="display: inline-block; background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">View Event Details →</a>
            </div>
            """

        html = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #f7fafc;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; padding: 30px; text-align: center; margin-bottom: 20px;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🚀 Webb Austin Tech Events</h1>
                    <p style="color: #e2e8f0; margin: 10px 0 0 0;">Your Weekly Tech Events Roundup</p>
                    <p style="color: #cbd5e0; margin: 5px 0 0 0; font-size: 14px;">{datetime.now().strftime('%B %d, %Y')}</p>
                </div>

                <!-- Events -->
                <div style="background: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #2d3748; margin-top: 0; margin-bottom: 20px; border-bottom: 3px solid #6b46c1; padding-bottom: 10px;">Upcoming Events ({len(events)})</h2>
                    {events_html}
                </div>

                <!-- Footer -->
                <div style="text-align: center; margin-top: 20px; color: #718096; font-size: 12px;">
                    <p>Automated weekly digest • Webb Austin Tech Events</p>
                    <p style="margin: 5px 0;">Visit <a href="{self.webb_url}" style="color: #6b46c1;">{self.webb_url}</a> for more</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_email(self, html_content, subject=None):
        """Send the email via Gmail SMTP."""
        if subject is None:
            subject = f"Webb Austin Tech Events - {datetime.now().strftime('%B %d, %Y')}"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            logging.info(f"Sending email to {self.recipient_email}")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            logging.info("Email sent successfully!")
            return True
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return False

    def run(self):
        """Main execution function."""
        logging.info("=== Webb Events Emailer Started ===")

        # Fetch events
        events = self.fetch_events()

        # Create HTML email
        html_content = self.create_html_email(events)

        # Send email
        success = self.send_email(html_content)

        if success:
            logging.info("=== Webb Events Emailer Completed Successfully ===")
        else:
            logging.error("=== Webb Events Emailer Failed ===")

        return success

def main():
    """Entry point for the script."""
    try:
        emailer = WebbEventsEmailer()
        emailer.run()
    except FileNotFoundError:
        logging.error("config.json not found. Please create it with your email credentials.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
