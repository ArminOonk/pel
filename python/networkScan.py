#!/usr/bin/python
import subprocess 
import xml.dom.minidom
import time
import datetime
import json
from subprocess import PIPE 
from subprocess import Popen 
import sys
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup 

from connect import *
import sendEmail
import os
import os.path


def beep():
	os.system("beep -f 784 -r 3 -l 100")
	time.sleep(0.1)
	os.system("beep -f 784 -l 600")
	os.system("beep -f 622 -l 600")
	os.system("beep -f 698 -l 600")
	os.system("beep -f 784 -l 200")
	time.sleep(.2)
	os.system("beep -f 698 -l 200")
	os.system("beep -f 784 -l 800")

def downloadMP3(text):
    language = "nl"

    url = "http://translate.google.com/translate_tts?ie=UTF-8&q="+str(text)+"&tl="+language
    print(url)

    r = requests.get(url)
    filename = str(text) + ".mp3"
    print(filename)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)
			
def getAddress():
	addressList = []
	pipe = Popen(['nmap', '-oX', '-', '-sn', '192.168.0.1/24'], stdout=PIPE)

	dom = xml.dom.minidom.parseString(pipe.stdout.read())
	for dhost in  dom.getElementsByTagName('host'):
		if dhost.getElementsByTagName('status')[0].getAttributeNode('state').value ==  'up':
			addrDict = {'mac': '', 'ip': ''}
			for a in dhost.getElementsByTagName('address'):
				if a.getAttributeNode('addrtype').value == 'mac':
					addrDict['mac'] = a.getAttributeNode('addr').value.lower()
				if a.getAttributeNode('addrtype').value == 'ipv4':
					addrDict['ip'] = a.getAttributeNode('addr').value
			addressList.append(addrDict)
	return addressList

def getAddressModem(modemUsername, modemPassword):
	try:
		r = requests.get('http://192.168.0.1/RgComputers.asp', auth=(modemUsername,modemPassword))
	except requests.exceptions.ConnectionError:
		return []
	soup = BeautifulSoup(r.text)
	addressList = []

	soupTables = soup.body.find('table', {"style" : "font-family: Helvetica;font-size:14"})
	for row in soupTables.findAll('tr'):
		col = row.findAll('td')
		if col[0].string != None and col[1].string != None:
			mac = col[0].string.strip()
			ip	= col[1].string.strip()
			if mac != 'MAC Address' or ip != 'IP Address':
				mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12] 
				addressList.append({'mac': mac.lower(), 'ip': ip})
	return addressList
	
hosts = getAddress()
hostsModem = getAddressModem(modemUsername, modemPassword)
#hostsModem = []

for modem in hostsModem:
	found = False
	for scan in hosts:
		if scan['mac'] == modem['mac']:
			found = True
	if not found:
		hosts.append(modem)

data = dict()
data.setdefault('TimeStamp', int(round(time.time())))
data.setdefault('Addresses', hosts)
dataJson = json.dumps(data)

import MySQLdb as mdb
con = mdb.connect('localhost', dbUsername, dbPassword, 'test');
	
with con: 
	cur = con.cursor(mdb.cursors.DictCursor)
	query = 'INSERT INTO `ConnectedHostsTimeSeries` (`Id` , `Time` , `Data`)VALUES (NULL , NOW(), \''+dataJson+'\');'
	print(query)
	cur.execute(query)
	
	isAlert = False
	
	# Set the status to In when we see the device
	for h in hosts:
		query = 'SELECT unix_timestamp(`LastSeen`),Name FROM ConnectedHosts WHERE MAC=\''+h['mac']+'\''

		#print(query)
		cur.execute(query)
		rows = cur.fetchall()

		if len(rows) > 0:
			lastSeenTime =  rows[0]["unix_timestamp(`LastSeen`)"]
			print("lastSeenTime: " + str(lastSeenTime) + " now: " + str(time.time()))
			print("Last seen: " + str(time.time() - lastSeenTime) + " seconds ago")
			
			print(rows[0])
			if rows[0]["Name"]:
				print("name: " + rows[0]["Name"])
				txt = rows[0]["Name"] + " is thuis"
				filename = txt + ".mp3"
				if not os.path.isfile(filename):
					print("File not found, downloading: " + filename)
					downloadMP3(txt)
				
				#os.system("mpg123 \"" + filename + "\"")
			else:
				print("Name is empty")
				
			query = 'UPDATE `ConnectedHosts` SET `Status` = \'In\',`LastSeen`=NOW(),`lastIP` = \''+h['ip']+'\' WHERE `MAC` = \''+h['mac']+'\''
			#print(query)
			cur.execute(query)
			
		else:
			query = 'UPDATE `ConnectedHosts` SET `Status` = \'Out\', `LastLeft`=NOW() WHERE NOT `MAC` = \'C4:17:FE:65:1E:8A\' AND `Status` = \'In\''
			#print(query)
			cur.execute(query)
			rows = cur.fetchall()
			
			if h['mac']:
				mail = sendEmail.sendEmail()
				mail.fromAddress(emailFrom)
				mail.toAddress(emailTo)
				mail.subject("Unknown device detected")
				mail.message("Unknown device: "+h['mac'])
				mail.send()
				
				query = "INSERT INTO `test`.`ConnectedHosts` (`Name`, `Device`, `MAC`, `LastSeen`, `LastLeft`, `Status`, `lastIP`) VALUES (\'"+h['mac']+"\', \'Unknown\', \'"+h['mac']+"\', NOW(), NOW(), \'In\', \'"+h['ip']+"\');";
				print(query)
				cur.execute(query)
				rows = cur.fetchall()
				beep()
				
	if isAlert:
		pass#beep()
