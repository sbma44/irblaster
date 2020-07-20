from http.server import BaseHTTPRequestHandler
import os, os.path
import time
import json
from urllib.parse import unquote, urlparse, parse_qs

import requests
#import paho.mqtt.client as mqtt

try:
    from local_settings import *
except:
    pass

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        d = parse_qs(self.path)
        for k in d:
            if type(d[k]) is list and len(d[k]) == 1:
                d[k] = d[k][0]
        d['device'] = d['/blaster?device']

        if d.get('device') == 'projector':
            if d.get('action') == 'on':
                print('projector on')
                requests.get('http://192.168.1.4:8044/msg?code=2A4C0286B430:DENON:48&simple=1&pass=XHV2HFCTyi')
                requests.get('http://192.168.1.4:8044/msg?code=CF20D:NEC:32&address=0x3000&simple=1&pass=XHV2HFCTyi')
            elif d.get('action') == 'off':
                print('projector off')
                PROJECTOR_OFF_URL = 'http://192.168.1.4:8044/msg?code=C728D:NEC:32&address=0x3000&simple=1&pass=XHV2HFCTyi'
                requests.get(PROJECTOR_OFF_URL)
                time.sleep(0.5)
                requests.get(PROJECTOR_OFF_URL)
                requests.get('http://192.168.1.4:8044/msg?code=2A4C028A0088:DENON:48&simple=1&pass=XHV2HFCTyi')
        elif d.get('device') == 'receiver':
            if d.get('action') == 'on':
                print('receiver on')
                requests.get('http://192.168.1.4:8044/msg?code=2A4C0286B430:DENON:48&simple=1&pass=XHV2HFCTyi')
            elif d.get('action') == 'off':
                print('receiver off')
                requests.get('http://192.168.1.4:8044/msg?code=2A4C028A0088:DENON:48&simple=1&pass=XHV2HFCTyi')
        elif d.get('device') == 'screen':
            if d.get('action') == 'down':
                print('screen down')
                requests.get('http://192.168.1.4:8044/json?simple=1&pass=XHV2HFCTyi&plain=[{data:[1292,442,1266,438,1268,440,1266,440,492,1204,490,1204,492,1204,490,1210,490,1206,1264,440,492,1206,490,1204,490,1206,1264,440,490,1204,1264,444,1266,440,1266,440,1268,440,490,1204,1264,442,1264,442,1266,440,490,1210,1264,440,1266,440,490,1204,492,1204,1264,440,492,1202,492,1204,1266,29696,1266,440,1266,440,1266,442,1264,440,492,1202,492,1204,492,1204,490,1208,490,1204,1266,438,492,1206,488,1206,490,1202,1268,442,490,1204,1266,442,1266,438,1266,440,1266,440,492,1204,1264,438,1268,440,1266,440,492,1208,1266,440,1266,442,490,1206,488,1204,1266,442,490,1204,490,1204,1266],type:\'raw\',khz:38}]')
            elif d.get('action') == 'up':
                print('screen up')
                requests.get('http://192.168.1.4:8044/json?simple=1&pass=XHV2HFCTyi&plain=[{data:[1326,434,1276,430,1276,430,1274,432,504,1162,532,1162,534,1162,534,1166,534,1160,534,1160,1308,428,504,1160,534,1162,1308,428,506,1158,1310,430,1280,426,1280,426,506,1158,1310,426,1280,426,1280,426,506,1158,1310,430,1280,426,506,1158,1312,426,506,1160,1310,424,508,1158,536,1158,1310,29652,1312,424,1282,424,1282,424,1284,424,506,1160,536,1158,536,1158,536,1160,536,1160,534,1160,1314,424,508,1158,534,1160,1310,424,506,1160,1312,426,1282,422,1282,424,506,1160,1310,424,1282,424,1282,424,506,1158,1312,428,1282,424,506,1158,1312,424,508,1156,1312,424,508,1160,536,1156,1312],type:\'raw\',khz:38}]')       
 
        self.send_response(200)
        self.send_header("Content-Type", "text/ascii")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        print(body)

        self.send_response(200)
        self.send_header("Content-Type", "text/ascii")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 8044), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
