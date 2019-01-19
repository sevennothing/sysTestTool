# -*- encoding: utf-8 -*-
#    __author__ = 'caijun.Li'
#    __date__ = '2019/1/19'
#    __Desc__ = 分析610A-8 内存泄露, 用于收集设备日志

import logging
import socketserver
import threading
import re

LOG_FILE = './log/mem.log'

logging.basicConfig(level=logging.INFO,
                    format='%(message)s',
                    datefmt='',
                    filename=LOG_FILE,
                    filemode='a')

global glogger
glogger = {}

global gDynamicAnalysiseTool

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def process_shape_log(self, matched):
        #print(matched.group())
        self.matched = 1
        return ""
        pass
    def handle(self):
        global glogger
        global gDynamicAnalysiseTool
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        
        msg=str(data)
        #pattern = re.compile(r'<(\S+)>(.*)')
        #print(msg)
        pattern = re.compile(r'<(\S+)>(\S+ \d+ \d+:\d+:\d+) (\S+) (.*)')
        matches = re.findall(pattern, msg)
        #print(matches)
        if(len(matches) == 0):
            return

        if matches[0][0] in glogger:
            self.matched = 0
            newmsg = re.sub("\[#\]", self.process_shape_log, matches[0][3])
            if(self.matched == 1):
                glogger[matches[0][0]]['waitData'] = 1
                glogger[matches[0][0]]['msg'] += newmsg
                return
            elif(glogger[matches[0][0]]['waitData'] == 1):
                ## 已经匹配完整的一条消息
                glogger[matches[0][0]]['waitData'] = 0
            else:
                ## 一条短消息
                glogger[matches[0][0]]['waitData'] = 0

            if(glogger[matches[0][0]]['timestamp']):
                glogger[matches[0][0]]['msg'] = matches[0][1] + " " + glogger[matches[0][0]]['msg'] + newmsg
            else:
                glogger[matches[0][0]]['msg'] = glogger[matches[0][0]]['msg'] + newmsg

            self.write_log(glogger[matches[0][0]]['logger'], glogger[matches[0][0]]['msg'])
            glogger[matches[0][0]]['msg'] = ""
        else:
            print( "%s : " % self.client_address[0], str(data))

        #logging.info(str(data))
#        socket.sendto(data.upper(), self.client_address)
    def write_log(self, logger, msg):
        logger.write(msg + '\n')
        gDynamicAnalysiseTool.input_data(msg)
        logger.flush()
        pass


class SyslogCollect(object):
    def __init__(self, dynamicAnalysiseTool, host='0.0.0.0', port=514, logfilePath='./log', 
                       logItem={"174":{'logfile':"mem.log", "timestamp":0}, 
                                "163":{'logfile':"fibmgmt.log","timestamp":1}},
                        ):
        global glogger
        global gDynamicAnalysiseTool
        self.port = port
        self.host = host
        self.logPath = logfilePath
        self.logItem = logItem
        for item in logItem:
            self.logItem[item]['logfile'] = self.logPath + '/' + self.logItem[item]['logfile']

            ''' 使用loggong '''
            #self.logger[item] = logging.getLogger("INFO")
            #self.logger[item].addHandler(logging.FileHandler(self.logItem[item]))
            self.logItem[item]['logger'] = open(self.logItem[item]['logfile'], 'a+',encoding="utf-8")
            self.logItem[item]['waitData'] = 0;  ## 有[#]时需要等待接收后面得数据
            self.logItem[item]['msg'] = "";      ## 完整得数据

                
        glogger = self.logItem
        gDynamicAnalysiseTool = dynamicAnalysiseTool
        #LOG_FILE = logfile
        
    def run(self):
        try:
            server = socketserver.UDPServer((self.host, self.port), SyslogUDPHandler)
            server.serve_forever(poll_interval=0.5)
        except (IOError, SystemExit):
            raise
        except KeyboardInterrupt:
            print ("Crtl+C Pressed. Shutting down.")
        pass


