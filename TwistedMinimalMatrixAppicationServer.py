#!/usr/bin/env python
from twisted.internet import protocol
from twisted.application.internet import TCPServer
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
import json
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from twisted.internet import defer
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
import urllib
from time import time

#TODO set debug flag for extended output
DEBUG=True
#TODO set port according to yaml config file
PORT=8111
#TODO set correct AS token according to yaml config file (as_token:.....)
AS_TOKEN="abcdefghijklmnopqrstuvwxyz"
#TODO set the ssh account USER@FQDN for the server running synapse or to None if running on the same server
MATRIX_REMOTE="user@your.server.de"  # account should be able to login w/o password, e.g. certificate based
#TODO set the AS user name to identify self originated events
WHOAMI="@tester:your.server.de"

TXN_ID=1

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def debugOut(func, text):
    global DEBUG
    if DEBUG:
        print "DEBUG: " + func
        print "---------------------------------"
        print text
        print "================================="


def sendText(_room, content):
    sendMessage(_room, content)


def sendNotice(_room, content):
    sendMessage(_room, content, tx_id=None, msg_type="m.notice")


def send_message_event(_room, _event, _tx_id=None):
    global AS_TOKEN, TXN_ID
    room_qutd = urllib.quote(_room)
    if _tx_id is None:
        _tx_id = str(TXN_ID) + str(int(time() * 1000))
    TXN_ID = TXN_ID + 1
    log.msg("send_message_event" + str(_event))
    httpRequest(
        url="http://127.0.0.1:8008/_matrix/client/api/v1/rooms/%s/send/m.room.message/%s?access_token=%s"
            % (room_qutd, _tx_id, AS_TOKEN),
        content=json.dumps(_event),
        headers={"Content-Type": ["application/json"]},
        method='PUT',
        req=None)


def sendMessage(_room, content, tx_id=None, msg_type="m.text"):
    send_message_event(_room
                , {
                       "msgtype": msg_type,
                       "body": content,
                  }
                , tx_id)


def get_html_content(html, body=None, msgtype="m.text"):
    return {
        "body": body if body else re.sub('<[^<]+?>', '', html),
        "msgtype": msgtype,
        "format": "org.matrix.custom.html",
        "formatted_body": html
    }


def sendHtml(_room, html, body=None, msgtype="m.text"):
    """Send an html formatted message.

    Args:
        html (str): The html formatted message to be sent.
        body (str): The body of the message to be sent (unformatted).
    """
    return send_message_event( _room, get_html_content(html, body, msgtype))


def setRoomName(room, name):
    setRoomState(room, name)


def setRoomTopic(room, content):
    setRoomState(room, content, state_type="topic")


def setRoomState(_room, content, state_type="name", state_key=""):
    global AS_TOKEN, TXN_ID
    room_qutd = urllib.quote(_room)
    httpRequest(
        url="http://127.0.0.1:8008/_matrix/client/api/v1/rooms/%s/state/m.room.%s/%s?access_token=%s"
            % (room_qutd, state_type, state_key, AS_TOKEN),
        content=json.dumps({
            state_type: content,
        }),
        headers={"Content-Type": ["application/json"]},
        method='PUT',
        req=None)


def httpRequest(url, content=None, headers={}, method='POST', req=None, callback=None):
    # Construct an Agent.
    agent = Agent(reactor)
    #data = urllib.urlencode(values)

    d = agent.request(method,
                      url,
                      Headers(headers),
                      StringProducer(content) if content else None)

    def handle_response(response):
        if response.code == 204:
            d = defer.succeed('')
        else:
            class SimpleReceiver(protocol.Protocol):
                def __init__(s, d):
                    s.buf = '';
                    s.d = d

                def dataReceived(s, data):
                    s.buf += data

                def connectionLost(s, reason):
                    # TODO: test if reason is twisted.web.client.ResponseDone, if not, do an errback
                    debugOut("rx http response", s.buf)
                    s.d.callback(s.buf)
                    if callback is not None:
                        callback(s.buf)

            d = defer.Deferred()
            response.deliverBody(SimpleReceiver(d))
            if req is not None:
                req.write(json.dumps({}))
                req.finish()
        return d

    d.addCallback(handle_response)
    return d


class RoomsPage(Resource):
    isLeaf = True
    roomsCb = None

    def render_GET(self, request):
        global AS_TOKEN
        alias = urllib.unquote(request.postpath[0])
        alias_localpart = alias.split(":")[0][1:]
        debugOut("Rooms GET" , alias)
        httpRequest(
            url="http://127.0.0.1:8008/_matrix/client/r0/createRoom?access_token=" + AS_TOKEN,
            content=json.dumps({
                "room_alias_name": alias_localpart
            }),
            headers={"Content-Type": ["application/json"]},
            method='POST',
            req=request,
            callback=self.roomsCb
        )
        return NOT_DONE_YET


class UsersPage(Resource):
    isLeaf = True
    usersCb = None

    def render_GET(self, request):
        global AS_TOKEN
        userid = urllib.unquote(request.postpath[0])
        userid_localpart = userid.split(":")[0][1:]
        debugOut("Users GET" , userid)
        httpRequest(
            url="http://127.0.0.1:8008/_matrix/client/r0/register?access_token=%s" % ( AS_TOKEN, ),
            content=json.dumps({
                "username": userid_localpart,
                "bind_email": False,
                "password": "ilovebananastoo",
                "auth": {
                    "example_credential": "verypoorsharedsecret",
                    "session": "xxxxx",
                    "type": "example.type.foo"
                }
            }),
            headers={"Content-Type": ["application/json"]},
            method='POST',
            req=request,
            callback=self.usersCb
        )
        return NOT_DONE_YET


# EXAMPLE CALLBACK
def checkJoin(ev):
    content = ev["content"]
    if content.has_key("membership"):
        if content["membership"] == "join":
            print "JOINING"

class TransactionsPage(Resource):
    isLeaf = True
    eventCb = None

    def render_PUT(self, request):
        global AS_TOKEN, WHOAMI
        tx_id = request.postpath[0]
        json_raw = request.content.getvalue()
        json_data = json.loads(json_raw)
        debugOut("transactions PUT", json.dumps(json_data, sort_keys=True, indent = 4, separators = (',', ': ')))
        events = json_data["events"]
        for event in events:
            if event["sender"]!=WHOAMI:
                if self.eventCb is None:
                    content = event["content"]
                    if content.has_key("membership"):
                        if content["membership"] == "join" and content.has_key("displayname"):
                            s = "Welcome %s!" % content["displayname"]
                            sendMessage(event["room_id"], s)
                else:
                    self.eventCb(event)

        return json.dumps({})


class ApplicationHome(Resource):
    def render_GET(self, request):
        return "<html><body>Welcome to the application server!</body></html>"

# use something like this if the synapse server resides on a remote server and we are behind a NAT
def startTunnelToMatrix():
    import os
    global PORT, MATRIX_REMOTE
    p = str(PORT)
    os.system("ssh -f %s -R %s:127.0.0.1:%s  -L 8008:127.0.0.1:8008 -N" % (MATRIX_REMOTE, p, p))

# call this if you hav a more complex twisted app with service.MultiService() on top
def init(application):
    global PORT, MATRIX_REMOTE
    root = ApplicationHome()
    root.putChild("rooms", RoomsPage())
    root.putChild("users", UsersPage())
    root.putChild("transactions", TransactionsPage())
    factory = Site(root)
    j = TCPServer(PORT, factory)
    j.setServiceParent(application)
    if MATRIX_REMOTE is not None:
        startTunnelToMatrix()

if __name__ == '__main__':
    from twisted.internet import reactor
    root = ApplicationHome()
    root.putChild("rooms", RoomsPage())
    root.putChild("users", UsersPage())
    tp = TransactionsPage()
    tp.eventCb = checkJoin
    root.putChild("transactions", tp)
    factory = Site(root)
    if MATRIX_REMOTE is not None:
        startTunnelToMatrix()
    reactor.listenTCP(PORT, factory)
    reactor.run()
