from flask import Flask, json
from flask_restful import reqparse, abort, Api, Resource
from flask_httpauth import HTTPBasicAuth
from gevent.pywsgi import WSGIServer
import ts3
import configuration


app = Flask(__name__)
auth = HTTPBasicAuth()
api = Api(app)

def establish_connection():
    ts3conn = ts3.query.TS3Connection(configuration.ip, configuration.port)
    ts3conn.login(client_login_name=configuration.client_login_name, client_login_password=configuration.client_login_password)
    ts3conn.use(sid=configuration.sid)
    ts3conn.clientupdate(client_nickname=configuration.client_nickname)
    return ts3conn

conn = establish_connection()
@auth.verify_password
def verify_password(username, password):
    user = configuration.api_user
    passx = configuration.api_password
    if username == user and password == passx:
        return True

class Channel(Resource):
    @auth.login_required
    def get(self, cid):
        try:
            channel = conn.channelinfo(cid=cid)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return channel.parsed, 200

    @auth.login_required
    def delete(self, cid):
        try:
            channel = conn.channeldelete(cid=cid, force=0)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return None, 204


class ClientInfo(Resource):
    @auth.login_required
    def get(self, clid):
        try:
            client = conn.clientinfo(clid=clid)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return client.parsed

class ClientList(Resource):
    @auth.login_required
    def get(self):
        try:
            clients = conn.clientlist()
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return clients.parsed

class ChannelList(Resource):
    @auth.login_required
    def get(self):
        try:
            channels = conn.channellist()
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return channels.parsed

class ClientMessage(Resource):
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('clid', type=int, help='clid')
        parser.add_argument('message', type=str, help='message')
        args = parser.parse_args()
        try:
            conn.sendtextmessage(targetmode=1, target=args['clid'], msg=args['message'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return 1,201

class ChannelTopic(Resource):
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cid', type=int)
        parser.add_argument('channel_topic', type=str)
        args = parser.parse_args()
        try:
            conn.channeledit(cid=args['cid'], channel_topic=args['channel_topic'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return 1,201

class ServerBanner(Resource):
    '''
    self.sender('serveredit virtualserver_hostbanner_gfx_url=' + bannerlink)
    '''
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        try:
            conn.serveredit(virtualserver_hostbanner_gfx_url=args['url'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return 1,201


class Welcome(Resource):
    def get(self):
        return None, 200


class Messages(Resource):
    '''
    '''
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cid', type=int)
        parser.add_argument('message', type=str)
        args = parser.parse_args()
        try:
            conn.sendtextmessage(cid=args['cid'], channel_topic=args['message'], target_mode=3)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return 1,201


class MessagesSubscribe(Resource):
    '''
    '''
    @auth.login_required
    def get(self):
        try:
            conn.servernotifyregister(event="textprivate")
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return None, 200

class GetMessages(Resource):
    '''
    '''
    def get(self):
        try:
            events = conn.wait_for_event(timeout=0.5)
        except ts3.TS3TimeoutError as msg:
            abort(404, message="{}".format(msg))
        return events.parsed, 200

class PokeClient(Resource):
    '''
    '''
    @auth.login_required
    def get(self, msg, clid):
        try:
            conn.clientpoke(msg=msg, clid=clid)
        except ts3.query.TS3QueryError as msg:
             abort(404, message="{}".format(msg))
        return None, 202

class MassPoke(Resource):
    @auth.login_required
    def get(self, msg):
        clients = conn.clientlist()
        try:
            for client in clients:
                conn.clientpoke(msg=msg, clid=client["clid"])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return None, 202

class KickUser(Resource):
    @auth.login_required
    def get(self, clid):
        try:
            conn.clientkick(reasonid = 4, clid=clid)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        return None, 202

api.add_resource(Welcome, '/')
api.add_resource(ChannelList, '/channels')
api.add_resource(Channel, '/channels/<cid>')
api.add_resource(ChannelTopic, '/channels/topic')
api.add_resource(ServerBanner, '/banner')
api.add_resource(ClientList, '/clients')
api.add_resource(ClientInfo, '/clients/<clid>')
api.add_resource(ClientMessage, '/clients/message')
api.add_resource(MessagesSubscribe, '/notifyregister')
api.add_resource(GetMessages, '/getmessages')
api.add_resource(PokeClient, '/poke/<msg>/<clid>')
api.add_resource(MassPoke, '/masspoke/<msg>')
api.add_resource(KickUser, '/kickuser/<clid>')

if __name__ == '__main__':
    http_server = WSGIServer(('', 9998), app)
    http_server.serve_forever()
