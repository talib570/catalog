from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime as func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category = Column(String(40))
    is_active = Column(String(1))
    is_delete = Column(String(1))


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    locallity = Column(String(250))
    logo = Column(String(250))
    start_year = Column(Date)
    game_id = Column(Integer, ForeignKey('game.id'))
    created_on = Column(DateTime, default=func.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('user.id'))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    game = relationship(Game)
    user = relationship(User, foreign_keys=[created_by])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'locallity': self.locallity,
            'id': self.id,
            'game': self.game.name,
            'logo': "http://localhost:5000/static/images/userimages/"+self.logo,
        }


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String(125), nullable=False)
    email = Column(String(250), nullable=False)
    phone = Column(String(15))
    picture = Column(String(250))
    skill_level = Column(String(25))
    summary = Column(String(250))
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship(Team)
    share_contact = Column(String(1))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    created_by = Column(Integer, ForeignKey('user.id'))
    created_on = Column(DateTime)
    user = relationship(User, foreign_keys=[created_by])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'summary': self.summary,
            'picture': "http://localhost:5000/static/images/userimages/"+self.picture,
            'id': self.id,
            'skill_level': self.skill_level,
            'team': self.team.name,
            'game': self.team.game.name,
        }


engine = create_engine('sqlite:///teamcatalog.db')


Base.metadata.create_all(engine)
