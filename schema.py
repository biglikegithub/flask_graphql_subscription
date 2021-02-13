import random
import graphene
from graphene.types.field import source_resolver
from rx import Observable


class Query(graphene.ObjectType):
    base = graphene.String()


class RandomType(graphene.ObjectType):
    booler = graphene.String()
    seconds = graphene.Int()
    random_int = graphene.Int()


# data = Observable.subscribe(observer=)

flag = True
ret = Observable.of(RandomType(seconds=1, booler=0))

source = Observable


class Subscription(graphene.ObjectType):

    count_seconds = graphene.Int(up_to=graphene.Int())

    random_int = graphene.Field(RandomType)
    print("random_int")
    print(count_seconds.args)

    def resolve_count_seconds(root, info, up_to=5):
        print("callled")
        print(up_to)
        return Observable.interval(1000)\
                         .map(lambda i: "{0}".format(i))\
                         .take_while(lambda i: int(i) <= up_to)

    def resolve_random_int(root, info):
        print("callled-1")
        # ret = Observable.interval(1000).map(lambda i: RandomType(seconds=i, random_int=random.randint(0, 500)))
        # print(ret)
        # Observable.interval(1000).map(lambda i: RandomType(seconds=i, random_int=random.randint(0, 500)))

        return ret

        # source.subscribe(on_next=lambda value: print("Received {0}".format(value)))
        return source


schema = graphene.Schema(query=Query, subscription=Subscription)
