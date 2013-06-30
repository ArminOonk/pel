#!/usr/bin/python
import smtplib
from connect import *

msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (emailUsername, ", ".join(emailRecipients), "Test Email", "Hoi")
  
# versturen

server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(emailUsername,emailPassword)  
server.sendmail(emailUsername, emailRecipients, msg)  
server.quit() 