from os import getenv, path
import smtplib
from email.message import EmailMessage
import magic
import mimetypes
import envconfiguration as config


class SMTPClient:
    def __init__(self):
        self.SMTP_SERVER = config.SMTP_SERVER
        self.SMTP_PORT = config.SMTP_PORT
        self.MAIL_ACCOUNT = config.MAIL_ACCOUNT
        self.MAIL_PASSWORD = config.MAIL_PASSWORD
        self.MAIL_FROM = config.MAIL_FROM
        self.toAddresses = []
        self.bccAddresses = []
        self.ccAddresses = []
        self.subject = 'Messagem enviada automáticamente pelo sistema'
        self.senderEmail = self.MAIL_FROM
        self.htmlMessage = ''
        self.textMessage = ''
        self.attachments = []

    def send(self):
        
        if len(self.toAddresses) == 0:
            print('Enter an email address for toAddresses')
            return False

        message = EmailMessage()
        message['Subject'] = self.subject
        message['From'] = self.senderEmail
        message['To'] = self.toAddresses
        message['Bcc'] = ', '.join(self.bccAddresses)
        message['Cc'] = ', '.join(self.ccAddresses)
        message.set_content(self.textMessage, subtype='plain')
        message.add_alternative(self.htmlMessage, subtype='html')
        
        for file_path in self.attachments:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            file_name = path.basename(file_path)
            file_type = magic.from_buffer(file_data, mime=True)
            extenssion = mimetypes.guess_extension(file_type)

            message.add_attachment(file_data, maintype=file_type, subtype=extenssion, filename=file_name)

        smtp = smtplib.SMTP(host=self.SMTP_SERVER, port=self.SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(self.MAIL_ACCOUNT, self.MAIL_PASSWORD)
        
        try:
            print('Sending email...')
            smtp.send_message(message)
            print('Email sent!')
            smtp.quit()
            return True
        except Exception as error:
            print(error)
            return False
       