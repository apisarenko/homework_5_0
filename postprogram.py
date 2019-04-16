import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_SMTP = "smtp.gmail.com"
GMAIL_IMAP = "imap.gmail.com"

LOGIN = 'login@gmail.com'
PASSWORD = 'qwerty'
SUBJECT = 'Subject'
RECIPIENTS = ['vasya@email.com', 'petya@email.com']
MESSAGE = 'Message'
HEADER = None


class PostProgram:
    def __init__(self, server_sending, server_receiving):
        self.server_sending = smtplib.SMTP(server_sending, 587)
        self.server_receiving = imaplib.IMAP4_SSL(server_receiving)

    def send_letter(self, message):
        self.server_sending.ehlo()  # Идентифицировать себя с клиентом smtp gmail.
        self.server_sending.starttls()  # Защитить нашу электронную почту с помощью шифрования TLS.
        self.server_sending.ehlo()  # Повторно идентифицировать себя как зашифрованное соединение.
        self.server_sending.login(LOGIN, PASSWORD)
        self.server_sending.sendmail(LOGIN, self.server_sending, message.as_string())
        self.server_sending.quit()

    def receiving_letter(self, criterion):
        self.server_receiving.login(LOGIN, PASSWORD)
        self.server_receiving.list()  # Выводит список ящиков в почтовом ящике.
        self.server_receiving.select('inbox')  # Подключаемся к папке входящие.
        result, data = self.server_receiving.uid('search', None, criterion)  # Выполняет поиск и возвращает UID писем.
        assert data[0], 'There are no letters with current header'
        latest_email_uid = data[0].split()[-1]
        result, data = self.server_receiving.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]  # Тело письма в необработанном виде.
        # Включает в себя заголовки и альтернативные полезные нагрузки
        email_message = email.message_from_string(raw_email)
        self.server_receiving.logout()
        return email_message


def main():
    # отправка писема
    mail_server = PostProgram(GMAIL_SMTP, GMAIL_IMAP)
    message = MIMEMultipart()
    message['From'] = LOGIN
    message['To'] = ', '.join(RECIPIENTS)
    message['Subject'] = SUBJECT
    message.attach(MIMEText(MESSAGE))

    # получение почты
    criterion = '(HEADER Subject {})'.format(HEADER) if HEADER else 'ALL'
    email_message = mail_server.receiving_letter(criterion)


if __name__ == '__main__':
    main()
