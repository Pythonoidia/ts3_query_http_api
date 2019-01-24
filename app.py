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

@auth.verify_password
def verify_password(username, password):
    user = configuration.api_user
    passx = configuration.api_password
    if username == user and password == passx:
        return True

class Channel(Resource):
    @auth.login_required
    def get(self, cid):
        conn = establish_connection()
        try:
            channel = conn.channelinfo(cid=cid)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return channel.parsed, 200

    @auth.login_required
    def delete(self, cid):
        conn = establish_connection()
        try:
            channel = conn.channeldelete(cid=cid, force=0)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return None, 204


class ClientInfo(Resource):
    @auth.login_required
    def get(self, clid):
        conn = establish_connection()
        try:
            client = conn.clientinfo(clid=clid)
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return client.parsed

class ClientList(Resource):
    @auth.login_required
    def get(self):
        conn = establish_connection()
        try:
            clients = conn.clientlist()
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return clients.parsed

class ChannelList(Resource):
    @auth.login_required
    def get(self):
        conn = establish_connection()
        try:
            channels = conn.channellist()
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return channels.parsed

class ClientMessage(Resource):
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('clid', type=int, help='clid')
        parser.add_argument('message', type=str, help='message')
        args = parser.parse_args()
        conn = establish_connection()
        try:
            conn.sendtextmessage(targetmode=1, target=args['clid'], msg=args['message'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return 1,201

class ChannelTopic(Resource):
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cid', type=int)
        parser.add_argument('channel_topic', type=str)
        args = parser.parse_args()
        conn = establish_connection()
        try:
            conn.channeledit(cid=args['cid'], channel_topic=args['channel_topic'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
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
        conn = establish_connection()
        try:
            conn.serveredit(virtualserver_hostbanner_gfx_url=args['url'])
        except ts3.query.TS3QueryError as msg:
            abort(404, message="{}".format(msg))
        finally:
            conn.quit()
        return 1,201


class Welcome(Resource):
    def get(self):
        return None, 200



api.add_resource(Welcome, '/')
api.add_resource(ChannelList, '/channels')
api.add_resource(Channel, '/channels/<cid>')
api.add_resource(ChannelTopic, '/channels/topic')
api.add_resource(ServerBanner, '/banner')
api.add_resource(ClientList, '/clients')
api.add_resource(ClientInfo, '/clients/<clid>')
api.add_resource(ClientMessage, '/clients/message')

if __name__ == '__main__':
  http_server = WSGIServer(('', 80), app)
  http_server.serve_forever()
