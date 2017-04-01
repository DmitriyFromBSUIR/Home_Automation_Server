import sys
import ujson
from tornado import gen
import tornado.options
import tornado.ioloop
import tornado.httputil
import tornado.httpclient
from tornado.escape import json_decode, json_encode
import ssl
import aiohttp

if sys.platform == 'win32':
    LinkAddressPackFilepath = "/home/root/Python_Workspace/HTTP_Client/LinkAddressPacket.json"
    WEB_APP_URI = "http://f06a164d.ngrok.io:80/LinkAddressPacketsHandler"
else:
    LinkAddressPackFilepath = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\LinkAddressPacket.json"
    WEB_APP_URI = "https://iot-tumbler.herokuapp.com/update_automation_server"

def read_json():
    with open(LinkAddressPackFilepath) as json_file:
        json_data = ujson.load(json_file)
        print(json_data)
        return json_data

@tornado.gen.coroutine
def json_fetch(http_client, body):
    ssl_cntx = ssl.SSLContext(ssl.CERT_NONE)
    headers = {
            'Content-Type': 'application/json'
    }
    '''
    async with aiohttp.ClientSession() as session:
        async with session.post(WEB_APP_URI, data=body) as resp:
            print(resp.status)
            print(await resp.text())
    '''
    response = yield http_client.fetch(WEB_APP_URI, method='POST', body=body, validate_cert=ssl_cntx, headers=headers)
    #response = tornado.httpclient.HTTPRequest(WEB_APP_URI, method='POST', body=body, headers="Content-Type: application/json")
    raise gen.Return(response)

@tornado.gen.coroutine
def request():
    data = read_json()
    body = json_encode(data)
    #http_response = yield json_fetch(http_client, body)
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_response = yield json_fetch(http_client, body)
    print(http_response.body)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    #http_client = tornado.httpclient.AsyncHTTPClient()
    #request(http_client)
    tornado.ioloop.IOLoop.instance().run_sync(request)