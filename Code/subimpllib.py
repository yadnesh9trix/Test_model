import imaplib
import email
import pandas as pd
import smtplib

# Function to connect to the email server and fetch mail subjects
def fetch_mail_subjects(email_address, password, imap_server):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, password)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()

    subjects = []

    for mail_id in mail_ids:
        result, data = mail.fetch(mail_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = msg['subject']
        subjects.append(subject)

    mail.logout()

    return subjects

def save_to_excel(subjects, output_file):
    df = pd.DataFrame({'Subject': subjects})
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    # Replace these variables with your email credentials
    email_address = 'yadnesh.kolhe@foxberry.in'
    password = 'Kolhe@4321'
    imap_server = 'outlook.office365.com'

    output_file = 'email_subjects.xlsx'

    subjects = fetch_mail_subjects(email_address, password, imap_server)
    save_to_excel(subjects, output_file)

    print(f"Mail subjects have been fetched and saved to {output_file}.")
