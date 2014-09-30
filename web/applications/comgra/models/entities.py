# coding: utf8
from applications.comgra.modules.sqlalchemy import *
db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
metadata=MetaData(db)
### end web2py specific code

# example of SQLAlchemy model in a web2py model

researcher = Table('researchers', metadata,
   Column('id', Integer),
   Column('name', String(40)),
   Column('email', String),
   Column('lattes', String),
)

article = Table('articles', metadata,
   Column('id', Integer),
   Column('title', String(40)),
   Column('publication_date', String),
)

publication = Table('publication', metadata,
   Column('id_author', ForeignKey('researchers.id')),
   Column('id_article', ForeignKey('articles.id')),
)
