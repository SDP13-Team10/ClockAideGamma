import string,time,datetime,serial,re, os
import sqlite3, usb, shutil, errno, subprocess, csv		# Database integration

from questionBank import QuestionBank
#from ClockAideModes import *
#from ClockAideHelpers import *

#----------------------------------
# Database initialization
db = sqlite3.connect("/home/pi/ClockAideGamma/ClockAideDatabase/ClockAideDB")
cursor = db.cursor()

startTime = 0
stopTime = 0
sessionCount = 0
sessionStart = 0

#----------------------------------
# Hardware initialization

BaudRate = 9600
keypadLocation = "/dev/ttyUSB0" # Every time it's reconnected the index increases /dev/ttyUSB# use ls /dev to check
motorLocation = "/dev/ttyACM0"  # Might depend on the plug /dev/ttyACM1 (Index reset to zero on new power up)
databaseLocation = "/home/pi/ClockAideGamma/ClockAideDatabase/ClockAideDB"

keypad = serial.Serial(keypadLocation,BaudRate)
motor = serial.Serial(motorLocation,BaudRate)
qBank = QuestionBank(databaseLocation)

#----------------------------------
# Quiz Mode parameters

question = 0
attempt = 0
correct = 0
incorrect = 0
answer = 0




currentTime = ""
id = ""
mode = ""
comm = ""

modes =	("NORMAL",  "CHECK_ID",  "READ", "SET", "TEACHER")

stuff =	{
	'00'  : "NORMAL", \
	'01'  : "CHECK_ID", \
	'02'  : "READ",\
	'03'  : "SET", \
	'04'  : "TEACHER", \
	'05'  : "GOOD", \
	'06'  : "WRONG", \

	'07'  : "WAKE_UP",\
	'08'  : "GET_TIME", \
	'09'  : "RESET", \
	'10' : "SPEAK_TIME"
	}
MODES =	{
	'0'  : "NORMAL", \
	'1'  : "CHECK_ID", \
	'2'  : "READ",\
	'3'  : "SET", \
	'4'  : "TEACHER"
	}

COMMAND = {
	'0'  : "GOOD", \
	'1'  : "WRONG", \
	'2'  : "WAKE_UP",\
	'3'  : "GET_TIME", \
	'4'  : "RESET", \
	'5'  : "SPEAK_TIME", \
	'8'  : "DATA"
	}
	
command = {
	"good"		: '0', \
	"wrong"		: '1', \
	"wake_up"	: '2',\
	"get_time"	: '3',\
	"reset"		: '4',\
	"speak_time"	: '5'
}

modeLookUp = {
	"normal"	: '0',\
	"check_id"	: '1',\
	"read"		: '2',\
	"set"		: '3',\
	"teacher"	: '4'
	}

namesID = {
	"123"  : "Eric", \
	"456"  : "Sachin", \
	"789"  : "Anita",\
	"321"  : "Joel", \
	"654"  : "Prof Leonard", \
	"987"  : "Prof Soules", \
	"852"  : "Megan Ferrari", \
        "222"  : "Prof Janaswamy", \
	"333"  : "Prof Hollot", \
	"444"  : "Prof Salthouse"
	}

def initialization():
	global mode
	global currentTime
	time.sleep(2)
	#keypad.flush()
	#motor.flush()
	
	currentTime = datetime.datetime.now()
	print(keypad.write(currentTime.strftime("%H, %M, %S, %d, %m, %Y")))
	print(motor.write(currentTime.strftime("%H, %M, %S, %d, %m, %Y")))
	
	time.sleep(2)
	
	mode = modes[0]
	
def normal():
	global comm
	print "in normal"
	try:
		print keypad.inWaiting()
		comm = COMMAND[str(keypad.read())]		## use different method other than stuff dictionary
		print "received" 
		print comm
		if comm == "SPEAK_TIME":
			speakTime(nowHour(), nowMinute())
			print(keypad.write(modeLookUp["normal"]))
			keypad.flushInput()
			comm = ""
			print comm
			return modes[0]
		elif comm == "WAKE_UP":					## send check ID signal to keypad and motor
			print(keypad.write(modeLookUp["check_id"]))
			print(motor.write(modeLookUp["check_id"]))
			
			return modes[1]						## return statements???
		elif comm == "EXIT":
			#quit()
			return modes[0]
		else:
			return modes[0]
			#return modes[3]	See read mode

	except KeyError:
		print "Error!!!"						## put some logging functionality
		
		return modes[0]

# -------------------------------------
# User Login
def userLogin():
 #global lockout
 global id
 #global admin

 s.write('\xFE\x01')
 s.write('\xFE\x0D')
# s.write('User Login      Enter Lunch #:')
 s.write('Enter Lunch #:')
 user = int(raw_input("Enter your lunch number: "))

 
 sql = "SELECT id FROM students WHERE id=?"
 auth = cursor.execute(sql, [(user)])
 userInput = str(user)
 cursor.execute('''SELECT * FROM students WHERE id='''+userInput)
 queryResult = cursor.fetchone()

 if queryResult is None:
 	queryResult = [-1,"-1"]

 if queryResult[0] == user:
   print "Welcome " + queryResult[1]
   print 'User authenticated. Starting ClockAide....'
   s.write('\xFE\x01')
   s.write('\xFE\x0C')
   s.write('Welcome         ' + queryResult[1])		# Shows user name
   #s.write('     User         Authenticated')
   time.sleep(2)
   id = user
   #normal()
   #modeSelect()		# Was switched back so that different users can log in
			# Placed a call for this in Normal mode
			# Turned off to allow login for Programming mode
 
 elif lockout != 3:
    lockout += 1
    print 'Invalid lunch number. Please try again....'
    s.write('\xFE\x01')
    s.write('Login Failed.   Try again...')
    time.sleep(1)
    userLogin()

 else:
   print 'Maximum attempts reached. Returning to normal mode...'
   s.write('\xFE\x01')
   s.write('Maximum attempts reached....')
   time.sleep(3)
   s.write('\xFE\x01')
   s.write('Returning to Normal Mode...')
   time.sleep(1)
   normal()
# -------------------------------------

def checkID():
	
	global id
	global name
	try:
		id = keypad.read(3)
		name = namesID[id]		## replace this with function to check input ID vs. database
		sql = "SELECT id FROM students WHERE id=?"
		auth = cursor.execute(sql, [(id)])
		cursor.execute('''SELECT * FROM students WHERE id='''+ id)
		queryResult = cursor.fetchone()
		#if name:
		if auth:
			print(keypad.write(command["good"]))			## Sends "Correct" Code to Keypad
			time.sleep(2)
			print(keypad.write(name))			## Sends Student Name to Keypad
			
			# beginning logging information
			
			return modes[int(keypad.read())]		## return statements???
		else:
			print(keypad.write(command["wrong"]))			## Sends "Correct" Code to Keypad
			time.sleep(2)
			return modes[0]	
		
	except KeyError:	
		print(keypad.write('6'))				## put some logging functionality
		return modes[1]							## return statements???
		
def read():
	global id
	global question
 	global correct		
	global incorrect
	global attempt		
	global sessionCount
	global sessionStart
	global stopTime
	mode = modes[2]

	question += 1
	print question

	sql = "SELECT * FROM students WHERE id=?"
	user = cursor.execute(sql, [("1")])
	start = time.ctime()				## Mark start time

	print(keypad.write(modeLookUp["read"]))
	print(motor.write(modeLookUp["read"]))
	time.sleep(2)
	qBank.generateTime()
	print(motor.write(readModeTime(id)))		## send time to be displayed to motor
	randomTime = qBank.getTimeTouple()
	print randomTime				## Show time in terminal
	#speakTime(randomTime[0],randomTime[1])
	readTime = keypad.read(5)			## include some timeout logic
	answer = readTime				## Latch user response

# Check time entered for correctness and send appropriate signal.
# Create a readtime function

	if checkReadTime(readTime,qBank.getTimeString()):
		correct += 1
		print correct
		print readTime		# Shows what was entered on the keypad

		sql = "INSERT INTO studentResponses (sid,studentResponse) VALUES (?,?)" # Save user input
		cursor.execute(sql, [(correct), (answer)])
		#db.commit()

		print(keypad.write(command["good"]))
		time.sleep(7)
		print(keypad.write(modeLookUp["normal"]))
		print(motor.write(modeLookUp["normal"]))

		stopTime = time.ctime()						# Save sessionLog
		sql = "INSERT INTO sessionLog (id, sessionStartTime, sessionEndTime, type) VALUES (?,?,?,?)"
		cursor.execute(sql, [(id), (start), (stopTime), (mode)]) # Need to figure out how to pull current user's ID (FK)
    		db.commit()

		return modes[0]
	else:
		incorrect += 1
		print incorrect
		print readTime		# Shows what was entered on the keypad

		sql = "INSERT INTO studentResponses (sid,studentResponse) VALUES (?,?)" # Save user input
		cursor.execute(sql, [(correct), (answer)])
		#db.commit()
	
		print(keypad.write(command["wrong"]))
		time.sleep(7)
		print(keypad.write(modeLookUp["normal"]))
		print(motor.write(modeLookUp["normal"]))

		stopTime = time.ctime()						# Save sessionLog
		sql = "INSERT INTO sessionLog (id, sessionStartTime, sessionEndTime, type) VALUES (?,?,?,?)"
		cursor.execute(sql, [(id), (start), (stopTime), (mode)]) # Need to figure out how to pull current user's ID (FK)
    		db.commit()
		return modes[0]

def set():
	global id
	global question
 	global correct		
	global incorrect
	global attempt		
	global sessionCount
	global sessionStart
	global stopTime
	mode = modes[3]

	question += 1
	print question

	sql = "SELECT * FROM students WHERE id=?"
	user = cursor.execute(sql, [("1")])
	start = time.ctime()				## Mark start time

	print(keypad.write(modeLookUp["set"]))
	print(motor.write(modeLookUp["set"]))
	time.sleep(2)
	#tme = currentTime.strftime("%H, %M")
	qBank.generateTime()
	senttime = setModeTime(id)
	print(keypad.write(senttime))
	randomTime = qBank.getTimeTouple()
	speakTime(randomTime[0],randomTime[1])
	motortime = qBank.getTimeString()
	answer = motortime				## Latch user response
	
	try:

		comm = COMMAND[str(keypad.read())]
	
		if comm == "GET_TIME":
			motortime = getTimeFromMotor()
	
		#else
		
		if senttime == motortime:				## Correct answer

			correct += 1
			print correct
			print motortime		# Shows what was entered on the knobs
						
			sql = "INSERT INTO studentResponses (sid,studentResponse) VALUES (?,?)" # Save user input
			cursor.execute(sql, [(correct), (answer)])
			db.commit()

			print(keypad.write(command["good"]))
			time.sleep(2)
			print(keypad.write(modeLookUp["normal"]))
			print(motor.write(modeLookUp["normal"]))
			
			stopTime = time.ctime()		# Save sessionLog
			sql = "INSERT INTO sessionLog (id, sessionStartTime, sessionEndTime, type) VALUES (?,?,?,?)"
			cursor.execute(sql, [(id), (start), (stopTime), (mode)]) # Need to figure out how to pull current user's ID (FK)
    			db.commit()

			return modes[0]
			
		else:							## Incorrect answer
			incorrect += 1
			print incorrect
			print motortime		# Shows what was entered on the keypad
	
			sql = "INSERT INTO studentResponses (sid,studentResponse) VALUES (?,?)" # Save user input
			cursor.execute(sql, [(correct), (answer)])
			db.commit()

			print(keypad.write(command["wrong"]))
			time.sleep(2)
			print(keypad.write(modeLookUp["normal"]))
			print(motor.write(modeLookUp["normal"]))

			stopTime = time.ctime()						# Save sessionLog
			sql = "INSERT INTO sessionLog (id, sessionStartTime, sessionEndTime, type) VALUES (?,?,?,?)"
			cursor.execute(sql, [(id), (start), (stopTime), (mode)]) # Need to figure out how to pull current user's ID (FK)
	    		db.commit()
			return modes[0]

	except KeyError:
		print "Error!!!"
		return modes[0]

def teacher():
	global comm
	global id
	mode = modes[4]
	
	print 'Admin Mode'
	print comm


        print(keypad.write(modeLookUp["teacher"]))
	time.sleep(2)		# Allows keypad to proceed to next line
	
	comm = COMMAND[str(keypad.read())]		# Receives command signal from keypad
	
	if comm == "DATA":
	  
	 print 'Exporting data'

###### Exporting data ####################	
	print 'Answers'					# Export user inputs
	data = cursor.execute("SELECT * FROM studentResponses")
	f = open('activity.csv', 'w')
	with open('./ClockAideDatabase/activity.csv', 'w') as f:
	 writer = csv.writer(f)
	 writer.writerow(['sid', 'qid', 'studentResponse'])	# Allows for custom column labels
	 writer.writerows(data)

	print 'Logs'					# Export session log
	data = cursor.execute("SELECT * FROM sessionLog")
	f = open('sessionLog.csv', 'w')
	
	with open('./ClockAideDatabase/sessionLog.csv', 'w') as f:
	 writer = csv.writer(f)
	 writer.writerow(['id','sessionStartTime', 'sessionEndTime', 'sessionID'])
	 writer.writerows(data)

	print 'users'					# Export lunch numbers
	data = cursor.execute("SELECT * FROM students")
	f = open('users.csv', 'w')
	
	with open('./ClockAideDatabase/student.csv', 'w') as f:
	 writer = csv.writer(f)
	 writer.writerow(['id', 'name', 'difficultyLevel'])
	 writer.writerows(data)
###### Exporting data ####################

############## Saving data to flash ####################	
	src0 = "./ClockAideDatabase/users.csv"
  	dst0 = "../../../../media/PENDRIVE" 
	
	src1 = "./ClockAideDatabase/activity.csv"
  	dst1 = "../../../../media/PENDRIVE" 

	src2 = "./ClockAideDatabase/sessionLog.csv"
  	dst2 = "../../../../media/PENDRIVE" 

	fileCopy(src0, dst0)
	fileCopy(src1, dst1)
	fileCopy(src2, dst2)

############## Saving data to flash ####################
	print(keypad.write(command["good"])) 		# Sends acknowledgement to keypad
	time.sleep(2)
	print(keypad.write(modeLookUp["normal"]))
	print(motor.write(modeLookUp["normal"]))	# Return to normal mode
	
	return modes[0]					

def getTimeFromMotor():
	return "4, 15"
		
def checkReadTime(readTime, sentTime):

	#Remove leading whitespaces:

	readTime = re.sub("^0+","",readTime)
	sentTime = re.sub("^0+","",sentTime)

	#Convert To Integers
	readHour = int(readTime.split(',')[0])
	readMinute = int(readTime.split(',')[1])

	sentHour = int(sentTime.split(',')[0])
	sentMinute = int(sentTime.split(',')[1])

	print "Check readTime entered"
	print "Time received: " + str(readHour) + "," + str(readMinute)
	print "Time sent: " + str(sentHour) + "," + str(sentMinute)
	# compare entered time with time given to student
	# return TRUE or False
	
	if readHour == sentHour and readMinute == sentMinute:
		return True
		
	else: 
		return False
	
	#return True
	
def readModeTime(ID):
	
	# Get difficulty level that the student is on
	# return time based on that level
	
	global qBank
	return qBank.getTimeString()
	
def setModeTime(ID):

	# Get difficulty level that the student is on
	# return time based on that level
	global qBank
	return qBank.getTimeString()
		
def nowHour():
	return datetime.datetime.now().strftime("%I")
	
def nowMinute():
	return datetime.datetime.now().strftime("%M")
	
def speakTime(hour,minute):

	hour = str(hour)
	minute = str(minute)

	if minute is not "0":
		minute = re.sub("^0+","",minute)

	hour = re.sub("^0+","",hour)

	hourFile = "~/VoiceMap/Hours/"+str(hour)+".wav"
	if minute is "0":
		minuteFile="~/VoiceMap/Wildcard/oclock.wav"
	else:
		minuteFile="~/VoiceMap/Minutes/"+str(minute)+".wav"

	playVoiceMap = "mplayer %s 1>/dev/null 2>&1 " + hourFile + " " + minuteFile
	os.system(playVoiceMap)

def fileCopy(src, dst):

 if dst != None:
  shutil.copy(src, dst)			# This will overwrite the file if it exists
  print "Copy Successful"


def main():
	
	global mode	
	initialization()

	while 1:
		if mode == "NORMAL":
			mode = normal()
		
		elif mode == "CHECK_ID":
			mode = checkID()
			
		elif mode == "READ":
			mode = read()
		
		elif mode == "SET":
			mode = set()
		
		elif mode == "TEACHER":
			mode = teacher()

main()
