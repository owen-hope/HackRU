#--------------------------------------------------
#version py 2.7
#--------------------------------------------------

import time
import threading
import datetime
from flask import Flask, request
from twilio import twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)

account_sid = //Enter your own twilio sid
auth_token = //Enter your own twilio auth-token
twilioPhoneNumber = '+19142651098'

client = TwilioRestClient(account_sid, auth_token)

notifications = {}
#K = phone # V = username
contacts = {}
admin = None

@app.route('/sms', methods=['POST'])
def sms():
	global twilioPhoneNumber
	global admin

	#store number and message from senders
	number = request.form['From']
	message_body = request.form['Body'].strip()

	#stores response for sender
	resp = twiml.Response()

	#adds people into the dictionary(database)
	if number not in contacts.keys():
		#checks to see if dict is empty for admin
		if len(contacts) == 0:
			admin = number
			client.messages.create(to=admin, from_=twilioPhoneNumber, body="For admin options send 'options'")

		#store a new user to dictionary
		contacts[number] = message_body

		#Notifies admin that new user has been added
		if number is not admin:
			client.messages.create(to = admin, from_ = twilioPhoneNumber, body = str(contacts[number]) + " has been added")

		#response back to sender
		resp.message("You've been added to {}'s class chat as {}".format(contacts[admin], contacts[number]))
		return str(resp)
	#resp.message('Hello {}, you said: {}'.format(number, message_body))

	#checks if number is admin
	if number == admin:
		respNum = None
		nameLength = None
		#chacks for special charcter for personal messages to students
		if message_body[0] == '@':
			bodyfromtext = message_body.split()
			name = bodyfromtext[0][1:]
			nameLength = len(name) + 1
			#find student based on name
			for tempNum in contacts.iterkeys():
				if name.lower() == contacts[tempNum].lower():
					respNum = tempNum
			#if name isn't found
			if respNum == None:
				resp.message("name not found")
				return str(resp)

			messageBody = " ".join(bodyfromtext)

			client.messages.create(to=respNum, from_= twilioPhoneNumber, body= messageBody[nameLength:])

	 	elif message_body[0] == '#':

	 		dateandtime(message_body)

		elif message_body.lower() == 'options':
			resp.message(	"These are all your options as admin:\n"+
							"@:direct message to student by username\n" +
							"#:sets notifications,(!)-optional for immediate notification along with setting the notification \n" +
							"ex:4/23/2017(!) 'Enter message here'\n" +
							"Users: lists usernames of students in the class")

		elif message_body.lower() == 'users':
			emptyString = ''
			for k, v in contacts.iteritems():
				if k == admin:
					continue
				else:
					emptyString += v+'\n'
			resp.message(emptyString)
			return str(resp)

		else:
			for respondNum in contacts.iterkeys():
				if respondNum == admin:
					continue
				else:
					client.messages.create(to=respondNum, from_= twilioPhoneNumber, body= 'From your teacher:\n' + message_body)

	else:
		client.messages.create(to=admin, from_=twilioPhoneNumber, body='From {}:\n{}'.format(contacts[number], message_body))




	return str(resp)


def dateandtime(body):
	global twilioPhoneNumber
	global admin
	FromBody = body.split()
	Date = None

	if FromBody[0][-1] == '!':
		Date = FromBody[0][1:-1]
		for respondNum in contacts.iterkeys():
			if respondNum == admin:
				continue
			else:
				client.messages.create(to=respondNum, from_= twilioPhoneNumber, body= 'Alert:\n{} {}'.format(Date, FromBody[1]))
	else:
		Date = FromBody[0][1:]

	date = Date.split('/')
	t = datetime.datetime(int(date[2]), int(date[0]), int(date[1]) - 1, 9)
	totalSecond = (t - datetime.datetime.now()).total_seconds()
	totalSecond = int(totalSecond)
	threading.Timer(totalSecond, lambda: massMessage(Date, FromBody[1])).start()

	client.messages.create(to=admin, from_= twilioPhoneNumber, body= 'Alert has been set')

def massMessage(string1, string2):
	global twilioPhoneNumber
	for respondNum in contacts.iterkeys():
		client.messages.create(to=respondNum, from_= twilioPhoneNumber, body= 'Alert:\n{} {}'.format(string1, string2))

if __name__ == '__main__':
	app.run()
