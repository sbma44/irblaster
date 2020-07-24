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
SCREEN_UP = '[{data:[1292,440,1264,442,1266,440,1264,442,490,1232,462,1232,462,1232,462,1236,462,1210,486,1232,1238,442,490,1232,462,1232,1238,442,490,1230,1238,444,1264,442,1266,440,490,1230,1240,440,1264,442,1266,440,490,1232,1238,444,1266,440,490,1206,1264,442,490,1230,1238,442,492,1208,486,1208,1262,29698,1264,442,1264,442,1264,442,1264,442,488,1220,474,1234,462,1232,462,1236,462,1232,462,1234,1238,440,490,1232,462,1232,1238,442,490,1232,1238,444,1264,440,1266,442,490,1232,1238,440,1266,440,1266,440,492,1230,1238,446,1264,442,490,1232,1238,442,490,1232,1238,442,490,1232,462,1210,1262],type:\'raw\',khz:38}]'
SCREEN_DOWN = '[{data:[698,440,492,1204,490,1232,1238,440,492,1204,490,1204,1264,29696,1266,440,1266,440,1266,440,1266,440,492,1206,488,1206,488,1206,490,1210,488,1206,1264,440,492,1204,490,1208,488,1208,1262,440,492,1230,1238,444,1266,440,1266,440,1266,440,492,1230,1238,440,1266,440,1266,440,492,1210,1264,440,1266,440,490,1232,464,1230,1240,440,492,1232,464,1230,1240,29696,1266,440,1266,440,1266,440,1266,442,490,1204,490,1206,488,1210,486,1210,488,1206,1264,440,490,1206,488,1232,462,1206,1266,440,490,1204,1266,442,1266,440,1266,440,1266,440,492,1230,1238,440,1266,440,1266,442,492,1208,1264,440,1266,440,490,1208,488,1208,1262,440,492,1204,490,1206,1264],type:\'raw\',khz:38}]'

def send(code):
    if '[{data:[' in code:
        code = 'plain={}'.format(code)
    else:
        code = 'code={}'.format(code)
    url = 'http://{}/msg?simple=1&pass={}&{}'.format(IRBLASTER_SERVER, IRBLASTER_PASSWORD, code)
    requests.get(url)

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
                for i in range(4):
                    send(SCREEN_DOWN)
                    time.sleep(0.5)
            elif d.get('action') == 'up':
                syslog.syslog('screen up')
                for i in range(4):
                    send(SCREEN_UP)
                    time.sleep(0.5)

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
