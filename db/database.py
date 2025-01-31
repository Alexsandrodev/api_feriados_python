from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

 
# Conexão com o PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost:5432/"
engine = create_engine(DATABASE_URL, client_encoding='utf8')
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
sessionLocal = sessionLocal()

