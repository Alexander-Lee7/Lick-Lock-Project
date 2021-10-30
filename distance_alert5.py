import time
import RPi.GPIO as GPIO
import smtplib
import ConfigParser

############################################################################
# Initialize variables
#
# pins for the ultrasonic module and buzzer
trigger = 7
echo = 11
buzzer = 12

# read INI file 
config_object = ConfigParser.ConfigParser()
config_object.read('mailinfo.ini')

# Sender info => sender@gmail.com, password
sender_id = config_object.get('mail', 'sender')
sender_pw = config_object.get('mail', 'pw')

# Recipient info => recipient@gmail.com
recipient_id = config_object.get('mail', 'recipient')

# email server and port
smtp_server = config_object.get('server', 'smtp_server')
smtp_port = config_object.get('server', 'smtp_port')

# email contents
msg = 'Subject: System Alert!!\r\nFrom: ' + sender_id + '\r\nTo: ' + recipient_id + '\r\nItem A from Room A has been removed from the wall!'

# email variables
sent_email = 0

###############################################################################
# functions
#
def get_time_interval():

	GPIO.output(trigger, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(trigger, GPIO.LOW)

	# start process
	start_time = time.time()
	while GPIO.input(echo) == 0:
		start_time = time.time()

	# echo arrival
	stop_time = time.time()
	while GPIO.input(echo) == 1:
		stop_time = time.time()
	
	return (stop_time-start_time)

def activate_buzzer():
	buzzerSound = GPIO.PWM(buzzer, 1000)
	buzzerSound.start(50)
	time.sleep(0.1)
	buzzerSound.stop()
	time.sleep(0.1)


def is_deadzone(dist):
	# Ultrasonic HC-SR04 sensor has a dead zone (MIN Range:2cm, MAX Range:400cm)
	if (dist < 2 or dist > 400):
		return True
	else:
		return False


###################################################################################
# Main process
#  
# setting 
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)

# SMTP session
server=smtplib.SMTP(smtp_server, smtp_port)
server.ehlo()
# for security
server.starttls()
server.ehlo()

# login to sender email account
server.login(sender_id, sender_pw)


try:
	while True:
  
		time_interval = get_time_interval()
		# formula to translate elapsed time into distance
		distance = round(34300/2 * time_interval, 1)

		if is_deadzone(distance):
			distance = 0

		if distance > 10: 
			activate_buzzer()
			 
			if sent_email == 0:
				# sends email
			 	server.sendmail(sender_id, recipient_id, msg)
				sent_email = 1
		else:
			sent_email = 0


		time.sleep(0.1)


except KeyboardInterrupt:
	pass

server.quit()
GPIO.cleanup()
