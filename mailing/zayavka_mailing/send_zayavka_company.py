import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr


def send_zayavka_company_email_(receiver_email: str, message_):
    """ FUNCTION FOR SENDING EMAIL"""
    try:
        from service.parser import ParseEnv
        sender_email = ParseEnv.EMAIL_
        password = ParseEnv.EMAIL_PASS
        # receiver_add = receiver_email
        smtp_server = smtplib.SMTP("mail.pcassa.ru", 587)
        smtp_server.starttls()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "ЗАЯВКА"
        msg['From'] = formataddr(("PCASSA MANAGER", sender_email))
        # msg['To'] = receiver_email
        # smtp_server.starttls() #setting up to TLS connection
        smtp_server.login(sender_email, password)  # logging into out email id
        text = "ЗАЯВКА"
        # link_for_verify = """Name {mes.acc_contact_name}
        #                    Address {mes.acc_address}
        #                    Country {mes.acc_country}
        #                    Inn {mes.acc_inn}
        #                    """.format(mes=message_)
        mes = message_
        html = f"""\
        <html>
          <head></head>
          <body>
                <h3><i>Name</i></h3> {mes.acc_contact_name}
                </br>
                <h3><i>Organization</i></h3> {mes.acc_org_name}
                </br>
                <h3><i>Phone</i></h3> {mes.acc_phone}
                </br>
                <h3><i>Address</i></h3> {mes.acc_address}
                </br>
                <h3><i>Country</i></h3> {mes.acc_country}
                </br>
                <h3><i>Inn</i></h3> {mes.acc_inn}
                </br>
                <h3><i>Email</i></h3> {mes.acc_email}
          </body>
        </html>
        """
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        # smtp_server.sendmail(sender_email, "pcassa.pcassa@mail.ru", msg.as_string())
        # smtp_server.sendmail(sender_email, "a.kondal@pcassa.ru", msg.as_string())
        # smtp_server.sendmail(sender_email, "Kochkanyan@gmail.com", msg.as_string())
        smtp_server.quit()
        print('SUCCESS EMAIL Sent')
        return True
    except Exception as e:
        print(e)
        return None


