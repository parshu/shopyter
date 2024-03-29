import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from tools.text_utils import toutf8

def mail(to_address, subject, text):
    msg = MIMEMultipart()
    msg['From'] = 'parashuram@gmail.com'
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(toutf8(text), 'html'))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('parashuram@gmail.com', 'u4muixarm7tdmi')
    mailServer.sendmail('parashuram@gmail.com', to_address, msg.as_string())
    mailServer.close()


if __name__ == '__main__':
    mail('nadahalli@gmail.com', 'test email', 'hello world')
