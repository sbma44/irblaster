from http.server import BaseHTTPRequestHandler
import os, os.path
import time
import json
from urllib.parse import unquote, urlparse, parse_qs
import syslog

import requests
#import paho.mqtt.client as mqtt

try:
    from local_settings import *
except:
    pass

PROJECTOR_ON = 'CF20D:NEC:32&address=0x3000'
PROJECTOR_OFF = 'C728D:NEC:32&address=0x3000'
RECEIVER_ROKU = '2A4C0286B430:DENON:48'
RECEIVER_POWER = '2A4C028A0088:DENON:48'
SCREEN_UP = '[{data:[1326,434,1276,430,1276,430,1274,432,504,1162,532,1162,534,1162,534,1166,534,1160,534,1160,1308,428,504,1160,534,1162,1308,428,506,1158,1310,430,1280,426,1280,426,506,1158,1310,426,1280,426,1280,426,506,1158,1310,430,1280,426,506,1158,1312,426,506,1160,1310,424,508,1158,536,1158,1310,29652,1312,424,1282,424,1282,424,1284,424,506,1160,536,1158,536,1158,536,1160,536,1160,534,1160,1314,424,508,1158,534,1160,1310,424,506,1160,1312,426,1282,422,1282,424,506,1160,1310,424,1282,424,1282,424,506,1158,1312,428,1282,424,506,1158,1312,424,508,1156,1312,424,508,1160,536,1156,1312],type:\'raw\',khz:38}]'
SCREEN_DOWN = '[{data:[1292,442,1266,438,1268,440,1266,440,492,1204,490,1204,492,1204,490,1210,490,1206,1264,440,492,1206,490,1204,490,1206,1264,440,490,1204,1264,444,1266,440,1266,440,1268,440,490,1204,1264,442,1264,442,1266,440,490,1210,1264,440,1266,440,490,1204,492,1204,1264,440,492,1202,492,1204,1266,29696,1266,440,1266,440,1266,442,1264,440,492,1202,492,1204,492,1204,490,1208,490,1204,1266,438,492,1206,488,1206,490,1202,1268,442,490,1204,1266,442,1266,438,1266,440,1266,440,492,1204,1264,438,1268,440,1266,440,492,1208,1266,440,1266,442,490,1206,488,1204,1266,442,490,1204,490,1204,1266],type:\'raw\',khz:38}]'

def send(code):
    if '[{data:[' in code:
        code = 'code={}'.format(code)
    else:
        code = 'plain={}'.format(code)
    requests.get('http://{IRBLASTER_SERVER}/msg?simple=1&pass={IRBLASTER_PASSWORD}&{CODE}', CODE=code, IRBLASTER_SERVER=IRBLASTER_SERVER, IRBLASTER_PASSWORD=IRBLASTER_PASSWORD)

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        d = parse_qs(self.path)
        for k in d:
            if type(d[k]) is list and len(d[k]) == 1:
                d[k] = d[k][0]
        d['device'] = d['/blaster?device']

        if d.get('device') == 'projector':
            if d.get('action') == 'on':
                syslog.syslog('projector on')
                send(RECEIVER_ROKU)
                send(PROJECTOR_ON)
            elif d.get('action') == 'off':
                syslog.syslog('projector off')
                for i in range(4):
                    send(PROJECTOR_OFF)
                    time.sleep(0.5)
                send(RECEIVER_POWER)
                for i in range(4):
                    send(SCREEN_UP)
                    time.sleep(0.5)
        elif d.get('device') == 'receiver':
            if d.get('action') == 'on':
                syslog.syslog('receiver on')
                send(RECEIVER_ROKU)
            elif d.get('action') == 'off':
                syslog.syslog('receiver off')
                send(RECEIVER_POWER)
        elif d.get('device') == 'screen':
            if d.get('action') == 'down':
                syslog.syslog('screen down')
                send(SCREEN_DOWN)
            elif d.get('action') == 'up':
                syslog.syslog('screen up')
                send(SCREEN_UP)

        self.send_response(200)
        self.send_header("Content-Type", "text/ascii")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 8044), GetHandler)
    syslog.syslog('starting server')
    server.serve_forever()