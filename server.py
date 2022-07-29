from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from flask import Flask, jsonify, request
from flask.views import MethodView
import pydantic
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

app = Flask('app')
bcrypt = Bcrypt(app)

BaseModel = declarative_base()

PG_DSN = 'postgresql://admin:1234@127.0.0.1:5431/flask_test'
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

class User(BaseModel):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=True, unique=True)
    password = Column(String, nullable=False)
    time = Column(DateTime, server_default=func.now())
    articles = relationship("Article")

class CreateUserModel(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.validator('password')
    def strong_password(cls,value):
        if len(value) < 8:
            raise ValueError('password to short')
        return value

class HttpError(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


@app.errorhandler(HttpError)
def http_error_handler(error):
    response = jsonify({
        'error': error.error_message
    })
    response.status_code = error.status_code
    return response

class UserView(MethodView):

    def get(self,user_id):
        with Session() as session:
            user = session.query(User).get(user_id)
            if user is None:
                raise HttpError(404, 'user not found')
            return jsonify({
                'name': user.name,
                'ts': user.time.timestamp()
            })

    def post(self):
        try:
            json_data_validate = CreateUserModel(**request.json).dict()
        except pydantic.ValidationError as er:
            raise HttpError(400, er.errors())
        password = json_data_validate['password']
        password:str = password.encode()
        password = bcrypt.generate_password_hash(password)
        password = password.decode()
        json_data_validate['password'] = password

        with Session() as session:
            user = User(**json_data_validate)
            session.add(user)
            try:
                session.commit()
                return jsonify({
                    'user_id': user.id
                })
            except IntegrityError as er:
                raise HttpError(400, 'user already exists')


class Article(BaseModel):

    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    header = Column(String(100), index=True, nullable=True, unique=True)
    description = Column(String, nullable=False)
    time = Column(DateTime, server_default=func.now())
    author = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Article "{self.header}">'

class CreateArticleModel(pydantic.BaseModel):
    header: str
    description: str
    author: int

    class Config:
        arbitrary_types_allowed = True

class ArticleView(MethodView):

    def get(self, article_id):
        with Session() as session:
            article = session.query(Article).get(article_id)
            if article is None:
                raise HttpError(404, 'article not found')
            return jsonify({
                'header': article.header,
                'description': article.description,
                'ts': article.time.timestamp()
            })

    def post(self):
        try:
            json_data_validate = CreateArticleModel(**request.json).dict()
        except pydantic.ValidationError as er:
            raise HttpError(400, er.errors())

        with Session() as session:
            auth_id = json_data_validate['author']
            if not session.query(User).get(auth_id):
                raise HttpError(404, 'user is not valid')
            article = Article(**json_data_validate)
            session.add(article)
            try:
                session.commit()
                return jsonify({
                    'article': article.id,
                    'header': article.header,
                    'description': article.description,
                })
            except IntegrityError as er:
                raise HttpError(400, 'such article already exists')

    def delete(self, article_id):
        with Session() as session:
            article = session.query(Article).get(article_id)
            if article is None:
                raise HttpError(404, 'article not found')
            else:
                session.delete(article)
                session.commit()
            return jsonify({'result': 'article deleted'})

    def put(self, article_id):
        try:
            json_data_validate = CreateArticleModel(**request.json).dict()
        except pydantic.ValidationError as er:
            raise HttpError(400, er.errors())
        with Session() as session:
            article = session.query(Article).get(article_id)
            if article is None:
                raise HttpError(404, 'article not found')
            if not session.query(User).get(json_data_validate['author']):
                raise HttpError(404, 'user is not valid')
            else:
                article.header = json_data_validate['header']
                article.description = json_data_validate['description']
                article.author = json_data_validate['author']
                session.add(article)
                session.commit()
            return jsonify({'result': 'article updated'})


BaseModel.metadata.create_all(engine)

app.add_url_rule('/users/', view_func=UserView.as_view('create_user'), methods=['POST'])
app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('get_user'), methods=['GET'])

app.add_url_rule('/articles/', view_func=ArticleView.as_view('create_article'), methods=['POST'])
app.add_url_rule('/articles/<int:article_id>', view_func=ArticleView.as_view('get_article'), methods=['GET'])
app.add_url_rule('/articles/delete/<int:article_id>', view_func=ArticleView.as_view('delete_article'), methods=['DELETE'])
app.add_url_rule('/articles/update/<int:article_id>', view_func=ArticleView.as_view('update_article'), methods=['PUT'])


app.run()

