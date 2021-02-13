import time
from graphql_client import GraphQLClient

ws = GraphQLClient('ws://localhost:5000/subscriptions')


def callback(_id, data):
    print("got new data..")
    print(f"msg id: {_id}. data: {data}")


query = """
  subscription{
  countSeconds(upTo: 10)
}
"""
query = """
  subscription{
  randomInt{
      booler  
    
  }
}
"""
sub_id = ws.subscribe(query, callback=callback)

while True:
    # sub_id = ws.subscribe(query, callback=callback)
    time.sleep(5)
    print("test")

    # later stop the subscription
ws.stop_subscribe(sub_id)
ws.close()
