import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from amqp_service.celery_app.celery_app import celery_decor


@celery_decor.task
def send_download_links(*, receiver_email: str, message: list):
    """ FUNCTION FOR SENDING EMAIL"""
    try:
        from service.parser import ParseEnv
        sender_email = ParseEnv.EMAIL_
        password = ParseEnv.EMAIL_PASS
        receiver_add = receiver_email
        smtp_server = smtplib.SMTP("mail.pcassa.ru", 587)
        smtp_server.starttls() #setting up to TLS connection
        ##############
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "DOWNLOAD PCASSA APPS"
        msg['From'] = formataddr(("PCASSA MANAGER", sender_email))
        msg['To'] = receiver_email
        #smtp_server.starttls() #setting up to TLS connection
        smtp_server.login(sender_email, password) #logging into out email id
        text = "DOWNLOAD PCASSA APPS"
        print(message)
        link_for_desktop_cassa_windows = u'<a href="pcassa.ru/{mes}">CLICK TO DOWNLOAD WINDOWS DESKTOP CASSA</a>'.format(mes=message[0][0]) \
        if message[0] else ''
        link_for_desktop_cassa_linux = u'<a href="{mes}">CLICK TO DOWNLOAD LINUX DESKTOP CASSA</a>'.format(mes=message[0][1]) \
        \
        if message[0] else ''
        link_for_mobile_cassa_android = u'<a href="{mes}">CLICK TO DOWNLOAD ANDROID MOBILE CASSA</a>'.format(mes=message[1][0]) \
        \
        if message[1] else ''
        link_for_mobile_cassa_ios = u'<a href="{mes}">CLICK TO DOWNLOAD IOS MOBILE CASSA</a>'.format(mes=message[1][1]) \
        \
        if message[1] else ''
        link_for_web_manager = u'<a href="{mes}">CLICK TO DOWNLOAD WEB MANAGER</a>'.format(mes=message[2][0]) \
        \
        if message[2] else ''
        link_for_mobile_manager_android = u'<a href="{mes}">CLICK TO DOWNLOAD ANDROID MOBILE MANAGER</a>'.format(mes=message[3][0]) \
        if message[3] else ''
        link_for_mobile_manager_ios = u'<a href="{mes}">CLICK TO DOWNLOAD IOS MOBILE MANAGER</a>'.format(mes=message[3][1]) \
        \
        if message[3] else ''
        html = f"""\
        <html>
          <head></head>
          <body>
                <h2 color='red'> PCASSA </h2>
               {link_for_desktop_cassa_windows if message[0] else ''}
               <br/>
               {link_for_desktop_cassa_linux if message[0] else ''}
               <br/>
               {link_for_mobile_cassa_android if message[1] else ''}
               <br/>
               {link_for_mobile_cassa_ios if message[1] else ''}
               <br/>
               {link_for_web_manager if message[2] else ''}
               <br/>
               {link_for_mobile_manager_android if message[3] else ''}
               <br/>
               {link_for_mobile_manager_ios if message[3] else ''}
          </body>
        </html>
        """
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        smtp_server.sendmail(sender_email, receiver_add, msg.as_string())
        smtp_server.quit()
        print('SUCCESS EMAIL Sent')
        return True
    except Exception as e:
        print(e)
        return False
