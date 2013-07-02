import smtplib
from connect import *
		
class sendEmail:
	fromAddr = ""
	toAddr = list()
	subject = ""
	message = ""
	
	def fromAddress(self, _fromAddress):
		self.fromAddr = _fromAddress
	
	def toAddress(self, _toAddress):
		self.toAddr.append(_toAddress)
	
	def subject(self, _subject):
		self.subject = _subject
		
	def message(self, _message):
		self.message = _message
	
	def send(self):		
		#msg = """\
		#From: %s
		#To: %s
		#Subject: %s
		#
		#%s
		#""" % (self.fromAddress, ", ".join(self.toAddress), self.subject, self.message)
		  
		# versturen

		headers = ["from: " + self.fromAddr, "subject: " + self.subject, "to: " + ", ".join(self.toAddr), "mime-version: 1.0", "content-type: text/html"]
		headers = "\r\n".join(headers)

		server = smtplib.SMTP('smtp.gmail.com:587')  
		server.starttls()  
		server.login(emailUsername,emailPassword)  
		server.sendmail(self.fromAddr, self.toAddr, headers + "\r\n\r\n" + self.message)  
		server.quit() 