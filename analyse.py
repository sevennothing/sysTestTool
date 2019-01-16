# coding:utf-8
import sys
import os


import shutil
import json
import time
import datetime
import re
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
 
#    __author__ = 'licj'
#    __date__ = '2019/1/12'
#    __Desc__ = 分析610A-8 内存泄露


class LROS_tool_project(object):
	def __init__(self):
		print("=====  LROS Analyse Tool ====")
		self.data={}
		self.data['AnalyseTime'] = str(datetime.datetime.now())
		self.data['sysinfo'] = {}
		self.data['total_count'] = 0
		self.data['program'] = []
		self.data['sysinfolog'] = []
		self.data['memlog'] = []
		self.data['meminfolog'] = []
		self.data['programLog'] = {}

		## 相对时间使能
		self.relative_time = 1

		self.vmItem = ['VmPeak','VmSize','VmLck','VmHWM',
		               'VmRSS','VmData','VmStk','VmExe','VmLib','VmPTE']

		'''
		这里的VmPeak代表当前进程运行过程中占用内存的峰值.
		VmSize代表进程现在正在占用的内存
		VmLck代表进程已经锁住的物理内存的大小.锁住的物理内存不能交换到硬盘.
		VmHWM是程序得到分配到物理内存的峰值
		VmRSS是程序现在使用的物理内存.
		VmData:表示进程数据段的大小.
		VmStk:表示进程堆栈段的大小.
		VmExe:表示进程代码的大小.
		VmLib:表示进程所使用LIB库的大小.

		'''
		self.viewVmItem = ['ts','VmPeak','VmSize','VmHWM','VmRSS','VmData']

		self.meminfoItemName = ['MemTotal', 'MemFree','Buffers','Cached','SwapCached','Active','Inactive',
							'HighTotal','HighFree','LowTotal','LowFree','SwapTotal','SwapFree',
							'Dirty','Writeback','AnonPages','Mapped','Slab','SReclaimable','SUnreclaim',
							'PageTables','NFS_Unstable','Bounce','WritebackTmp','CommitLimit','Committed_AS',
							'VmallocTotal','VmallocUsed','VmallocChunk'
							]

		pass

	def get_system_base_info(self):
		pattern = re.compile(r'INFO: SYSTEM-INFO (.*)')
		matches = re.findall(pattern, self.oriData)
		self.data['sysinfo']['uname'] = str(matches[0])

		### slabinfo Item collect
		pattern = re.compile(r'slabinfo-key: .*# (.*)')
		matches = re.findall(pattern, self.oriData)
		#print(matches)
		if (len(matches) == 0):
			self.data['sysinfo']['slabItem'] = []
			return
		pattern3 = re.compile(r'\S+')
		m = re.findall(pattern3, matches[0])
		self.data['sysinfo']['slabItem'] = m
		pass

	def get_dest_pid(self):
		pattern = re.compile(r'INFO: check (\S+) pid is (\d+)')
		matches = re.findall(pattern, self.oriData)
		for item in matches:
			program = {}
			#print(item)
			program['name'] = item[0]
			program['pid'] = item[1]
			self.data['program'].append(program)

		#print(json.dumps(self.data))

		'''
		searchObj = re.search(r'INFO: check ' + programName + ' pid is ' + programPid, self.oriData)
		if not searchObj:
			program = {}
			program['name'] = programName
			program['pid'] = progrmaPid
			self.data['program'].append(program)
			json.dumps(self.data)
		'''

		pass

	def get_total_count(self):
		pattern = re.compile(r'!!! Check (\d+) when (\d+);(.*)load average: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)')
		#pattern = re.compile(r'!!! Check (\d+) when (\d+);')
		matches = re.findall(pattern, self.oriData)
		for item in matches:
			sysinfo = {}
			sysinfo['itlem']=item[0]
			sysinfo['ts']=item[1]
			sysinfo['average_1_min']=item[3]
			sysinfo['average_5_min']=item[4]
			sysinfo['average_15_min']=item[4]
			self.data['sysinfolog'].append(sysinfo)
			self.data['total_count'] += 1

		#print(json.dumps(self.data))
		pass

	def get_mem_usage(self):
		pattern = re.compile(r'Mem: *(\d+) *(\d+) *(\d+) *(\d+) *(\d+)')
		matches = re.findall(pattern, self.oriData)
		for item in matches:
			#print(item)
			meminfo = {}
			meminfo['used'] = item[1]
			meminfo['free'] = item[2]
			meminfo['shared'] = item[3]
			meminfo['buffers'] = item[4]
			self.data['memlog'].append(meminfo)
		### parse system info ###
		self.data['sysinfo']['memTotal'] = matches[0][0]

		#print(json.dumps(self.data))
		pass
	def get_meminfo(self):
		pattern = re.compile(r'MemTotal: *(\d+) kB *'\
			                   'MemFree: *(\d+) kB *'\
			                   'Buffers: *(\d+) kB *'\
			                   'Cached: *(\d+) kB *'\
			                   'SwapCached: *(\d+) kB *'\
			                   'Active: *(\d+) kB *'\
			                   'Inactive: *(\d+) kB *'\
			                   'HighTotal: *(\d+) kB *'\
			                   'HighFree: *(\d+) kB *'\
			                   'LowTotal: *(\d+) kB *'\
			                   'LowFree: *(\d+) kB *'\
			                   'SwapTotal: *(\d+) kB *'\
			                   'SwapFree: *(\d+) kB *'\
			                   'Dirty: *(\d+) kB *'\
			                   'Writeback: *(\d+) kB *'\
			                   'AnonPages: *(\d+) kB *'\
			                   'Mapped: *(\d+) kB *'\
			                   'Slab: *(\d+) kB *'\
			                   'SReclaimable: *(\d+) kB *'\
			                   'SUnreclaim: *(\d+) kB *'\
			                   'PageTables: *(\d+) kB *'\
			                   'NFS_Unstable: *(\d+) kB *'\
			                   'Bounce: *(\d+) kB *'\
			                   'WritebackTmp: *(\d+) kB *'\
			                   'CommitLimit: *(\d+) kB *'\
			                   'Committed_AS: *(\d+) kB *'\
			                   'VmallocTotal: *(\d+) kB *'\
			                   'VmallocUsed: *(\d+) kB *'\
			                   'VmallocChunk: *(\d+) kB *'\
			                )
		matches = re.findall(pattern, self.oriData)
		for item in matches:
			meminfo = {}
			meminfo['MemTotal'] = item[0]
			meminfo['MemFree'] = item[1]
			meminfo['Buffers'] = item[2]
			meminfo['Cached'] = item[3]
			meminfo['SwapCached'] = item[4]
			meminfo['Active'] = item[5]
			meminfo['Inactive'] = item[6]
			meminfo['HighTotal'] = item[7]
			meminfo['HighFree'] = item[8]
			meminfo['LowTotal'] = item[9]
			meminfo['LowFree'] = item[10]
			meminfo['SwapTotal'] = item[11]
			meminfo['SwapFree'] = item[12]
			meminfo['Dirty'] = item[13]
			meminfo['Writeback'] = item[14]
			meminfo['AnonPages'] = item[15]
			meminfo['Mapped'] = item[16]
			meminfo['Slab'] = item[17]
			meminfo['SReclaimable'] = item[18]
			meminfo['SUnreclaim'] = item[19]
			meminfo['PageTables'] = item[20]
			meminfo['NFS_Unstable'] = item[21]
			meminfo['Bounce'] = item[22]
			meminfo['WritebackTmp'] = item[23]
			meminfo['CommitLimit'] = item[24]
			meminfo['Committed_AS'] = item[25]
			meminfo['VmallocTotal'] = item[26]
			meminfo['VmallocUsed'] = item[27]
			meminfo['VmallocChunk'] = item[28]

			self.data['meminfolog'].append(meminfo)

		pass

	def get_program_mem_usage(self, programName):
		#pattern = re.compile(r'Name:.*' + programName +'\n' + 'VmPeak:.*(\d+).*' + 'Name:.*' + programName + ' END', re.DOTALL | re.S)
		#pattern = re.compile(r'Name:.*mand\nVmPeak:.*(\d+).*' + 'Name:mand END', re.DOTALL | re.S)
		#pattern = re.compile(r'Name:.*mand.*Name:mand.*END', re.DOTALL | re.S)
		#pattern = re.compile(r'Name:.*' + programName + '.*Name:.*' + programName +'.*END', re.DOTALL)
		#pattern = re.compile(r'Name:.*mand\n((\S+):.*(\d+) kB\n)*Name:.*mand.*END')
		#pattern = re.compile(r'Name:.*mand(.*)')
		pattern = re.compile(r'Name:.*' + programName + '(.*)')
		#patternVm = re.compile(r'  ')
		patternVm = re.compile(r'.*VmPeak:[^1-9]*(\d+) kB VmSize:[^1-9]*(\d+) kB '\
								'VmLck:[^1-9]*(\d+) kB VmHWM:[^1-9]*(\d+) kB '\
								'VmRSS:[^1-9]*(\d+) kB VmData:[^1-9]*(\d+) kB '\
								'VmStk:[^1-9]*(\d+) kB VmExe:[^1-9]*(\d+) kB '\
								'VmLib:[^1-9]*(\d+) kB VmPTE:[^1-9]*(\d+) kB')
		matches = re.findall(pattern, self.oriData)
		#print(matches)
		self.data['programLog'][programName] = []
		for titem in matches:
			#print(titem)
			programlog = {}
			m = re.findall(patternVm, titem)
			#print(m)
			programlog['VmPeak'] = m[0][0]
			programlog['VmSize'] = m[0][1]
			programlog['VmLck'] = m[0][2]
			programlog['VmHWM'] = m[0][3]
			programlog['VmRSS'] = m[0][4]
			programlog['VmData'] = m[0][5]
			programlog['VmStk'] = m[0][6]
			programlog['VmExe'] = m[0][7]
			programlog['VmLib'] = m[0][8]
			programlog['VmPTE'] = m[0][9]
			self.data['programLog'][programName].append(programlog)

		pass

	def get_slab_used_info(self):
		patternstr = "slabinfo: 0 0 "
		for item in self.data['sysinfo']['slabItem']:
			patternstr += " *(\d+)"
		patternstr += " *"
		patternSlab = re.compile(patternstr)
		matches = re.findall(patternSlab, self.oriData)
		self.data['slabinfolog'] = []
		for item in matches:
			self.data['slabinfolog'].append(item)

		pass

	def get_iostat_info(self):
		patternIostatItem = re.compile(r'Device: *(\S+) *(\S+) *(\S+) *(\S+) *(\S+)')
		matcheItem = re.search(patternIostatItem, self.oriData).groups()
		#print(matcheItem)
		self.data['sysinfo']['iostatItem'] = list(matcheItem)
		self.data['sysinfo']['blockItem'] = []

		pattern = re.compile(r'mtdblock(\d+) *(\d.\d+) *(\d.\d+) *(\d.\d+) *(\d+) *(\d+)')
		matches = re.findall(pattern, self.oriData)
		self.data['iostatlog'] = {}
		for item in matches:
			blockItem = 'mtdblock' + str(item[0])
			if not blockItem in self.data['iostatlog']:
				self.data['iostatlog'][blockItem] = []
				self.data['sysinfo']['blockItem'].append(blockItem)
			self.data['iostatlog'][blockItem].append(item[1:])

		pass

	## 清洗数据
	def pre_process_data(self, data_path):
		if not os.path.exists(data_path):
			print("NOT FOUND Data File:" + data_path)
			return -1
		try:
			self.oriDataFile = open(data_path, 'r')
		except:
			print("file Open error:", e)

		self.oriData = self.oriDataFile.read()

		### 适配syslog远程日志

		self.oriData = self.oriData.replace('[#]\n','')
		self.oriData = self.oriData.replace('#012\n','\n')
		self.oriData = self.oriData.replace('#011',' ')
		self.oriData = self.oriData.replace('state_machine_r','fibmgmt')

		#'''
		with open('tmp.log', 'w') as f:
			f.write(self.oriData)
		f.close()
		#'''
		#sys.exit()


		self.get_system_base_info()
		self.get_dest_pid()
		self.get_total_count()
		self.get_mem_usage()
		self.get_meminfo()
		self.get_iostat_info()
		self.get_slab_used_info()

		self.ts = []
		for its in self.data['sysinfolog']:
			if(self.relative_time):
				self.ts.append(int(its['ts']) - int(self.data['sysinfolog'][0]['ts']))
			else:
				self.ts.append(int(its['ts']))

		for program in self.data['program']:
			self.get_program_mem_usage(program['name'])

		pass

	def save_data_to_json_file(self, dstFile):
		## 清洗过的数据存盘
		with open(dstFile, 'w', encoding='utf-8') as json_file:
			json_file.write(json.dumps(self.data, indent=4, ensure_ascii=False))
		json_file.close()
		pass

	def save_meminfo_to_csv_data_file(self):
		if(len(self.data['meminfolog']) == 0):
			return
		meminfo = {}
		for item in self.meminfoItemName:
			meminfo[item] = []
		mdata = {}
		mdata['ts'] = self.ts
		mdata['usedPercentage'] = []

		for itemlog in self.data['meminfolog']:
			for item in self.meminfoItemName:
				meminfo[item].append(itemlog[item])
			mdata['usedPercentage'].append((int(itemlog['MemTotal']) - int(itemlog['MemFree']) - int(itemlog['Buffers']) - int(itemlog['Cached']))/int(itemlog['MemTotal']))


		for item in self.meminfoItemName:
			mdata[item]=meminfo[item]

		df = pd.DataFrame(mdata)
		try:
			df.to_csv("meminfo.csv", index=False, sep=',')
		except:
			print("meminfo.csv FAILED", E)

		pass
	def save_slabinfo_to_csv_data_file(self):
		if(len(self.data['slabinfolog']) == 0):
			return
		slabinfo = {}
		slabinfo['ts'] = self.ts
		slabinfo['sum'] = []
		for item in self.data['sysinfo']['slabItem']:
			slabinfo[item] = []
		for itemlog in self.data['slabinfolog']:
			sum = 0
			for index,item in enumerate(self.data['sysinfo']['slabItem']):
				slabinfo[item].append(itemlog[index])
				sum += int(itemlog[index])
			slabinfo['sum'].append(sum)

		df = pd.DataFrame(slabinfo)
		try:
			df.to_csv("slabinfo.csv", index=False, sep=',')
		except:
			print("slabinfo.csv FAILED", e)

		pass


	def save_blockn_iostatinfo_to_csv_data_file(self, blockItem):
		iostatinfo = {}
		iostatinfo['ts'] = self.ts
		for item in self.data['sysinfo']['iostatItem']:
			iostatinfo[item] = []

		for itemlog in self.data['iostatlog'][blockItem]:
			for index,item in enumerate(self.data['sysinfo']['iostatItem']):
				iostatinfo[item].append(itemlog[index])

		if(len(self.ts) > len(iostatinfo['tps'])):
			iostatinfo['ts'] = self.ts[0:len(iostatinfo['tps'])]
		df = pd.DataFrame(iostatinfo)
		try:
			df.to_csv( blockItem + ".csv", index=False, sep=',')
		except:
			print(blockItem + ".csv FAILED", E)

		pass

	def save_iostatinfo_to_csv_data_file(self):
		if(len(self.data['iostatlog']) == 0):
			return

		for blockItem in self.data['sysinfo']['blockItem']:
			self.save_blockn_iostatinfo_to_csv_data_file(blockItem)

		pass
	
	def save_program_data_to_csv_data_file(self):
		VmPeak = {}
		VmSize = {}
		VmLck = {}
		VmHWM = {}
		VmRSS = {}
		VmData = {}
		VmStk = {}
		VmExe = {}
		VmLib = {}
		VmPTE = {}
		for program in self.data['program']:
			prname = program['name']
			VmPeak[prname] = []
			VmSize[prname] = []
			VmLck[prname] = []
			VmHWM[prname] = []
			VmRSS[prname] = []
			VmData[prname] = []
			VmStk[prname] = []
			VmExe[prname] = []
			VmLib[prname] = []
			VmPTE[prname] = []
			for item in self.data['programLog'][prname]:
				VmPeak[prname].append(item['VmPeak'])
				VmSize[prname].append(item['VmSize'])
				VmLck[prname].append(item['VmLck'])
				VmHWM[prname].append(item['VmHWM'])
				VmRSS[prname].append(item['VmRSS'])
				VmData[prname].append(item['VmData'])
				VmStk[prname].append(item['VmStk'])
				VmExe[prname].append(item['VmExe'])
				VmLib[prname].append(item['VmLib'])
				VmPTE[prname].append(item['VmPTE'])

			#print("=============>" + prname)
			df = pd.DataFrame({'ts':self.ts,
							   'VmPeak':VmPeak[prname],
				               'VmSize': VmSize[prname],
				               'VmLck': VmLck[prname],
				               'VmHWM': VmHWM[prname],
				               'VmRSS': VmRSS[prname],
				               'VmData': VmData[prname],
				               'VmStk': VmStk[prname],
				               'VmExe': VmExe[prname],
				               'VmLib': VmLib[prname],
				               'VmPTE': VmPTE[prname]
				               })
			try:
				df.to_csv(prname + ".csv", index=False, sep=',')
			except:
				print(prname + " FAILED", E)

		pass

	def save_data_to_csv_data_file(self):
		self.save_meminfo_to_csv_data_file()
		#self.save_program_data_to_csv_data_file()
		self.save_slabinfo_to_csv_data_file()

		pass

	def view_program_mem(self, programName):
		#self.df[programName] = pd.Series(self.data['programLog'][programName], self.ts)		
		#print(self.df[programName])
		#print(self.df[programName].describe())

		self.df[programName] = pd.read_csv(programName + '.csv', index_col=0, usecols=self.viewVmItem)
		'''
		plt.figure()
		plt.xlabel("timestamp")
		plt.ylabel("mem KB")
		plt.title(programName)
	
		plt.plot(self.df[programName])
		#self.df[programName].plot()
		#plt.show()
		'''
		fig = self.df[programName].plot(kind="line",title=programName,logy=True,subplots=True)
		#fig.set_ylabel("MEM with KB")

		pass
	def view_mem_info(self):
		self.df['meminfo'] = pd.read_csv('meminfo.csv', index_col=0, 
										  usecols=['ts','MemFree','Buffers','Cached','Active','Inactive','usedPercentage'])
		'''
		plt.figure()
		plt.xlabel("timestamp")
		plt.ylabel("mem KB")
		plt.title("meminfo")
		plt.plot(self.df['meminfo'])
		'''
		fig = self.df['meminfo'].plot(kind="line",title="meminfo",logy=False, subplots=True)
		#fig.set_ylabel("MEM with KB")

		pass
	def view_slab_info(self):
		if not os.path.exists('slabinfo.csv'):
			print("NOT FOUND Data File:slabinfo.csv")
			return -1
		self.df['slabinfo'] = pd.read_csv('slabinfo.csv', index_col=0,
										   usecols=['ts','sum'])
		fig = self.df['slabinfo'].plot(kind="line",title="slabinfo",logy=False, subplots=False)

		'''
		## 堆积柱状图
		usecols=['ts']
		for col in self.data['sysinfo']['slabItem']:
			if(col == "sum"):
				continue
			usecols.append(col)

		self.df['slabinfoAll'] = pd.read_csv('slabinfo.csv', index_col=0,
										   usecols=usecols)
		self.df['slabinfoAll'].drop(np.arange(1, self.data['total_count'] - 1, 30))
		#ax1 = self.df['slabinfoAll'].plot(kind="bar",title="slabinfoAll",logy=False, stacked=True, subplots=False)
		'''
		### 找到增长最快的列数据，并绘制
		declist = []
		for index,col in enumerate(self.data['sysinfo']['slabItem']):
			val = abs(int(self.data['slabinfolog'][0][index]) - int(self.data['slabinfolog'][-1][index]))
			declist.append(val)

		posmax = declist.index(max(declist))
		
		posMaxVal = declist[posmax]

		declist[posmax] = 0; ### 为找出第二个较大值
		pos2 = declist.index(max(declist))
		pos2Val = declist[pos2] 
		declist[pos2] = 0; ### 为找出第三个较大值
		pos3 = declist.index(max(declist))

		print("slabinfo 从 " + str(self.ts[0]) + " 到 " + str(self.ts[-1]))
		print("slabinfo 中变化最快：" + self.data['sysinfo']['slabItem'][posmax] + "=" + str(posMaxVal))
		print("slabinfo 中变化第二快：" + self.data['sysinfo']['slabItem'][pos2] + "=" + str(pos2Val))
		print("slabinfo 中变化第三快：" + self.data['sysinfo']['slabItem'][pos3] + "=" + str(declist[pos3]))

		specCols = ['ts', self.data['sysinfo']['slabItem'][posmax],self.data['sysinfo']['slabItem'][pos2],self.data['sysinfo']['slabItem'][pos3]]
		if not 'size-256' in specCols:
			specCols.append("size-256")

		self.df['slabinfoSpec'] = pd.read_csv('slabinfo.csv', index_col=0,
										   usecols=specCols)

		fig = self.df['slabinfoSpec'].plot(kind="line",title="slabinfoSpec",logy=False, subplots=False,marker='*')

		pass

	def view_blockn_iostat_info(self, blockItem):
		if not os.path.exists(blockItem + '.csv'):
			print("NOT FOUND Data File:" + blockItem + ".csv")
			return -1

		usecols = ['ts']
		usecols += self.data['sysinfo']['iostatItem']
		self.df[blockItem] = pd.read_csv(blockItem + '.csv', index_col=0,
										   usecols=usecols)

		fig = self.df[blockItem].plot(kind="line",title=blockItem, logy=False, subplots=True)

		pass

	def view_iostat_info(self):
		for blockItem in self.data['sysinfo']['blockItem']:
			self.view_blockn_iostat_info(blockItem)
		pass

	def data_view(self):
		self.df = {}

		self.view_mem_info()
		self.view_slab_info()
		self.view_iostat_info()

		for program in self.data['program']:
			prname = program['name']
			self.view_program_mem(prname)

		plt.show()

		pass

if __name__ == "__main__":
	print(datetime.datetime.now())

	prj = LROS_tool_project()
	prj.pre_process_data("./mem.log")

	prj.save_data_to_json_file("./mem.json")
	prj.save_data_to_csv_data_file()
	prj.save_iostatinfo_to_csv_data_file()

	prj.data_view()