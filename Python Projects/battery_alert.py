import psutil
import time
import smtplib
from email.message import EmailMessage
from plyer import notification

LOW_BATTERY_THRESHOLD = 40
CHECK_INTERVAL = 60

EMAIL_SENDER = 'sender@gmail.com'
EMAIL_PASSWORD = 'xxxxxxxxxxxx'
EMAIL_RECEIVER = 'receiver@gmail.com'

def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def send_email_notification(subject, message):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def monitor_battery():
    last_plugged = None
    low_battery_alert_sent = False
    
    while True:
        battery = psutil.sensors_battery()
        if battery is None:
            time.sleep(CHECK_INTERVAL)
            continue

        percent = battery.percent
        plugged = battery.power_plugged

        if last_plugged is None:
            last_plugged = plugged
        elif plugged != last_plugged:
            if plugged:
                send_desktop_notification(
                    'Charger Connected',
                    f'Charging started ({percent}%)'
                )
                send_email_notification(
                    'Charger Connected',
                    f'Charger plugged in at {percent}%'
                )
            else:
                send_desktop_notification(
                    'Charger Disconnected',
                    f'Running on battery ({percent}%)'
                )
                send_email_notification(
                    'Charger Disconnected',
                    f'Charger unplugged at {percent}%'
                )
            
            last_plugged = plugged

        if not plugged:
            if percent <= LOW_BATTERY_THRESHOLD and not low_battery_alert_sent:
                send_desktop_notification(
                    'Low Battery Warning',
                    f'Battery is low: {percent}%'
                )
                send_email_notification(
                    'Low Battery Alert',
                    f'Battery level is low: {percent}%'
                )
                low_battery_alert_sent = True
            elif percent > LOW_BATTERY_THRESHOLD:
                low_battery_alert_sent = False
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    monitor_battery()
