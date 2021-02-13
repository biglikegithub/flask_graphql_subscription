from flask import Flask
# from graphql.backend import GraphQLCoreBackend
from flask_sockets import Sockets
from graphql_ws.gevent import GeventSubscriptionServer

from schema import schema, RandomType, source, Subscription, ret
from overidenview import OveridenView


# class CustomBackend(GraphQLCoreBackend):
#     def __init__(self, executor=None):
#         super().__init__(executor)
#         self.execute_params['allow_subscriptions'] = True


app = Flask(__name__)
app.debug = True
app.add_url_rule('/graphql', view_func=OveridenView.as_view('graphql', schema=schema,  graphiql=True))

sockets = Sockets(app)
subscription_server = GeventSubscriptionServer(schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'

i = 0


@app.route('/<i>')
def hello_world(i: int):
    i = int(i)
    i += 1
    # Subscription.random_int()
    # source.from_([i, "Beta", "Gamma", "Delta", "Epsilon"])
    # ret.subscribe(on_next=lambda value: print("Received {0}".format(value)),
    #               on_completed=lambda: print("Done!"),
    #               on_error=lambda error: print("Error Occurred: {0}".format(error))
    #               )
    ret.pipe(RandomType(seconds=1, booler=1233))
    return 'Hello, World!'


@sockets.route('/subscriptions')
def echo_socket(ws):
    print(ws)
    subscription_server.handle(ws)
    print("test subscription")
    return ["success"]


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
