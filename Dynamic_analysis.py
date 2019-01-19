import sqlite3
import re
import _thread
import threading
import time
import signal

 
#    __author__ = 'licj'
#    __date__ = '2019/1/12'
#    __Desc__ = 分析610A-8 内存泄露

class Data_store(object):
	def __init__(self, dbname):
		self.conn = sqlite3.connect(dbname)
		print("opened database " + dbname + " successfully")
		self.sqlQuque = []
		pass

	def create_program_tab(self, name, columns):
		sqlstr = 'CREATE TABLE IF NOT EXISTS ' + name + ' (TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP'
		for cl in columns:
			sqlstr += ',' + cl + ' INT NOT NULL'
		sqlstr += ');'
		#print(sqlstr)
		self.join_store_data(sqlstr)
		pass

	def insert_program_data(self, name, columns, vals):
		self.create_program_tab(name, columns)
		sqlstr = 'INSERT INTO ' + name + ' ('
		for cl in columns:
			sqlstr += cl + ','

		sqlstr = sqlstr[0:-1]
		sqlstr += ") VALUES ("
		for vl in vals:
			sqlstr += vl + ','
		sqlstr = sqlstr[0:-1]
		sqlstr += ');'
		#print(sqlstr)
		self.join_store_data(sqlstr)

		pass
	def commit_store_data(self):
		print("==== COMMIT STORE DATA =====")
		print(self.sqlQuque)
		'''
		c = self.conn.cursor()
		c.execute(sqlstr)
		self.conn.commit()
		'''

	def join_store_data(self, sqlstr):
		#c.execute(sqlstr)
		#self.conn.commit()
		self.sqlQuque.append(sqlstr)

		pass

global is_run 
is_run = True

class ThreadStoreData(threading.Thread):
	def __init__(self, threadID, name, dataStore, interval=10):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.interval = interval
		self.dataStore = dataStore

	def run(self):
		global is_run
		print("Start Thread " + self.name)

		try:
			while is_run:
				time.sleep(self.interval)
				self.dataStore.commit_store_data()

		except (IOError, SystemExit):
			raise
		except KeyboardInterrupt:
			print ("Crtl+C Pressed. Shutting down.")

		print("Stop Thread " + self.name)


def signal_handler(signum, frame):
    global is_run
    is_run = False

class Dynamic_analysis(object):
	def __init__(self):
		#self.patternPrgram = re.compile(r'Name:[ \t]*' + '(\S+)[ \t]*' + '(\S+:[ \t]*\d+)?')
		self.patternPrgram = re.compile(r'Name:[ \t]*' + '(\S+)' + '(.*)')

		self.dataStore = Data_store("E://mem.db")

		signal.signal(signal.SIGINT, signal_handler)
		signal.signal(signal.SIGTERM, signal_handler)

		self.threadDataStore = ThreadStoreData(1, "dataStore", self.dataStore, 5)
		self.threadDataStore.start()

		pass

	def wait_stop_analysis(self):
		print("wait stop analysis")
		self.threadDataStore.join()
		pass

	def match_program(self, msg):
		matches = re.search(self.patternPrgram, msg)
		if(matches == None):
			return
		if(len(matches.groups()) == 0):
			return
		#print(matches)
		newmsg = re.sub(r'[ \t]*', '', matches[1])
		#print(newmsg)

		pname = matches[0]
		obj1 = newmsg.split('kB')
		#print(obj1)
		clname = []
		clval = []
		for item in obj1:
			obj2 = item.split(':')
			#print(obj2)
			if(len(obj2) < 2):
				continue
			clname.append(obj2[0])
			clval.append(obj2[1])

		#print(clname)
		#print(clval)

		self.dataStore.insert_program_data(pname, clname, clval)
		pass

	def input_data(self, msg):
		self.match_program(msg)

		pass
