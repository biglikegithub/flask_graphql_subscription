from flask import Flask
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView
from flask import json, request, session
import json
from flask_graphql_auth import (
    AuthInfoField,
    GraphQLAuth,
    get_raw_jwt,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    query_header_jwt_required,
    mutation_jwt_refresh_token_required,
    mutation_jwt_required
)
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'munguu'
app.config["JWT_SECRET_KEY"] = "MUNGUU"

auth = GraphQLAuth(app)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    email = Column(String(100))
    stores = relationship('Store', backref='owner')


class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node, )


class StoreObject(SQLAlchemyObjectType):
    class Meta:
        model = Store
        interfaces = (graphene.relay.Node,)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserObject)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = User.query.filter_by(username=username).first()
        if user:
            return CreateUser(user=user)
        user = User(username=username, password=password, email=email)
        if user:
            db_session.add(user)
            db_session.commit()
        return CreateUser(user=user)


class AuthMutation(graphene.Mutation):
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String()
        password = graphene.String()

    def mutate(self, info, username, password):
        user = User.query.filter_by(username=username, password=password).first()
        print(user)
        if not user:
            raise Exception('Authenication Failure : User is not registered')
        return AuthMutation(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username)
        )


class ProtectedStore(graphene.Union):
    class Meta:
        types = (StoreObject, AuthInfoField)


class CreateStore(graphene.Mutation):
    store = graphene.Field(ProtectedStore)

    class Arguments:
        name = graphene.String(required=True)
        user_id = graphene.Int(required=True)
        token = graphene.String()

    @mutation_jwt_required
    def mutate(self, info, name, user_id):
        store = Store(name=name, user_id=user_id)
        if store:
            db_session.add(store)
            db_session.commit()
        return CreateStore(store=store)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    auth = AuthMutation.Field()
    protected_create_store = CreateStore.Field()


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    print(dir(SQLAlchemyConnectionField))

    all_users = SQLAlchemyConnectionField(UserObject)
    # all_stores = SQLAlchemyConnectionField(StoreObject)
    all_stores = SQLAlchemyConnectionField(StoreObject)
    get_store = graphene.Field(type=ProtectedStore, token=graphene.String(), id=graphene.Int())

    @query_header_jwt_required
    def resolve_get_store(self, info, id):
        print(info.field_name)
        store_qry = StoreObject.get_query(info)
        storeval = store_qry.filter(Store.id.contains(id)).first()
        store_qry = StoreObject.query()
        print(store_qry)
        return storeval

    @query_header_jwt_required
    def resolve_all_stores(self, info, **kwargs):
        print(info.field_name)
        print(get_raw_jwt())
        store_qry = StoreObject.get_query(info)
        # storeval = store_qry.filter(Store.id.contains(id)).first()
        return store_qry

    # @query_header_jwt_required
    # def resolve_all_users(self, info,**kwargs):
    #     print(info.field_name)
    #     store_qry = UserObject.get_query(info)
    #     return store_qry


schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)


@app.route('/')
def home():
    return 'home'


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True)
