#!/usr/bin/env python3
"""
Test script for Webb Events Emailer
Run this to test the system before scheduling
"""

import sys
import json
from webb_events_emailer import WebbEventsEmailer

def test_configuration():
    """Test if configuration is properly set up."""
    print("🔧 Testing configuration...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        required_fields = ['webb_url', 'sender_email', 'sender_password', 'recipient_email']
        missing_fields = []

        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
            elif config[field] in ['your_email@gmail.com', 'your_app_password_here', '']:
                print(f"   ⚠️  {field} needs to be configured")
                return False

        if missing_fields:
            print(f"   ❌ Missing required fields: {', '.join(missing_fields)}")
            return False

        print("   ✅ Configuration looks good!")
        return True

    except FileNotFoundError:
        print("   ❌ config.json not found")
        return False
    except json.JSONDecodeError:
        print("   ❌ config.json is not valid JSON")
        return False

def test_scraping():
    """Test if we can fetch events from Webb."""
    print("\n🌐 Testing web scraping...")
    try:
        emailer = WebbEventsEmailer()
        events = emailer.fetch_events()

        if events:
            print(f"   ✅ Successfully found {len(events)} events!")
            print("\n   Preview of events:")
            for i, event in enumerate(events[:3], 1):
                print(f"\n   Event {i}:")
                print(f"   📌 Title: {event.get('title', 'N/A')}")
                print(f"   📅 Date: {event.get('date', 'N/A')}")
                print(f"   🔗 URL: {event.get('url', 'N/A')}")
            return True, events
        else:
            print("   ⚠️  No events found. This could mean:")
            print("      - Webb's website structure changed (you may need to update selectors)")
            print("      - There are no upcoming events listed")
            print("      - The website is blocking our requests")
            return False, []

    except Exception as e:
        print(f"   ❌ Error during scraping: {e}")
        return False, []

def test_email_generation(events):
    """Test HTML email generation."""
    print("\n📧 Testing email generation...")
    try:
        emailer = WebbEventsEmailer()
        html = emailer.create_html_email(events)

        if html and len(html) > 100:
            print("   ✅ HTML email generated successfully!")
            print(f"   📏 Email size: {len(html)} characters")
            return True
        else:
            print("   ❌ Email generation failed or produced invalid output")
            return False

    except Exception as e:
        print(f"   ❌ Error generating email: {e}")
        return False

def test_full_run():
    """Test the complete email sending process."""
    print("\n🚀 Running full system test (will send actual email)...")
    response = input("   Do you want to send a test email? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        try:
            emailer = WebbEventsEmailer()
            success = emailer.run()

            if success:
                print("\n   ✅ Test email sent successfully!")
                print("   📬 Check your inbox!")
                return True
            else:
                print("\n   ❌ Failed to send test email")
                print("   💡 Check the logs in webb_emailer.log for details")
                return False

        except Exception as e:
            print(f"\n   ❌ Error sending email: {e}")
            return False
    else:
        print("   ⏭️  Skipped email sending test")
        return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Webb Austin Events Emailer - System Test")
    print("=" * 60)

    # Test 1: Configuration
    config_ok = test_configuration()
    if not config_ok:
        print("\n❌ Configuration test failed. Please update config.json and try again.")
        sys.exit(1)

    # Test 2: Web scraping
    scraping_ok, events = test_scraping()

    # Test 3: Email generation
    email_ok = test_email_generation(events)

    # Test 4: Full run (optional)
    if config_ok and email_ok:
        full_run_ok = test_full_run()
    else:
        full_run_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Configuration:    {'✅' if config_ok else '❌'}")
    print(f"Web Scraping:     {'✅' if scraping_ok else '⚠️ '}")
    print(f"Email Generation: {'✅' if email_ok else '❌'}")
    print(f"Full System:      {'✅' if full_run_ok else '⏭️ '}")
    print("=" * 60)

    if config_ok and email_ok:
        print("\n✨ System is ready! You can now:")
        print("   1. Run 'python3 scheduler.py' to start the weekly scheduler")
        print("   2. Or run 'python3 webb_events_emailer.py' for a one-time email")
    else:
        print("\n⚠️  Please fix the issues above before running the scheduler.")

if __name__ == "__main__":
    main()
