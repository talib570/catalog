from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime as func

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String(125), nullable=False)
    username = Column(String(30), nullable=False)
    password = Column(String(32), nullable=False)
    email = Column(String(250), nullable=False)
    phone = Column(String(15))
    picture = Column(String(250))
    skill_level = Column(String(25))
    summary = Column(String(250))
    age = Column(Integer)
    share_contact = Column(String(1))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    created_on = Column(DateTime)


class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category = Column(String(40))
    created_on = Column(DateTime, default=func.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('player.id'))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    player = relationship(Player, foreign_keys=[created_by])


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    locallity = Column(String(250))
    logo = Column(String(250))
    start_year = Column(Date)
    game_id = Column(Integer, ForeignKey('game.id'))
    created_on = Column(DateTime, default=func.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('player.id'))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    game = relationship(Game)
    player = relationship(Player, foreign_keys=[created_by])


class TeamPlayers(Base):
    __tablename__ = 'team_player'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    is_active = Column(String(1))
    is_delete = Column(String(1))
    created_on = Column(DateTime, default=func.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('player.id'))
    creator = relationship(Player, foreign_keys=[created_by])
    team = relationship(Team)
    player = relationship(Player, foreign_keys=[player_id])


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey('team.id'))
    team2_id = Column(Integer, ForeignKey('team.id'))
    venue = Column(String(250))
    game_type = Column(String(80))
    start_time = Column(DateTime, default=func.datetime.utcnow)
    end_time = Column(DateTime, default=func.datetime.utcnow)
    t1_score = Column(Integer)
    t2_score = Column(Integer)
    is_active = Column(String(1))
    is_delete = Column(String(1))
    created_on = Column(DateTime, default=func.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('player.id'))
    creator = relationship(Player, foreign_keys=[created_by])
    team1 = relationship(Team, foreign_keys=[team1_id])
    team2 = relationship(Team, foreign_keys=[team2_id])


engine = create_engine('sqlite:///gamingevents.db')


Base.metadata.create_all(engine)
