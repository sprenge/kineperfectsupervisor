import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, config, email_server):
    # SMTP server configuration
    ec = config["emailservers"][email_server]

    sender_password = ec["password"]  # Be cautious about storing passwords in plaintext

    # Create the email
    message = MIMEMultipart()
    message["From"] = ec["sender_email"]
    message["To"] = ec["recipient_email"]
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server
        with smtplib.SMTP(ec["smtp_server"], ec["smtp_port"]) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(ec["sender_email"], sender_password)
            server.sendmail(
                ec["sender_email"], ec["recipient_email"], message.as_string()
            )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
