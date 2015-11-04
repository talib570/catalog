from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Player, Game, Base

engine = create_engine('sqlite:///gamingevents.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# adds new player
player = Player(name="Talib Allauddin", username="talib_570", password='78def760e9ed7c5adabf491ad99ff590', picture='static/images/talib.jpg', skill_level='Entry Level', summary='N/A', age=25, is_active='1', is_delete='0', phone='+923430505458', email='talib_570@live.com', share_contact='1')
session.add(player)
session.commit()


# adds game 1
game1 = Game(name='Need For Speed Most Wanted', category='Racing', created_by=1, is_active='1', is_delete='0')
session.add(game1)
session.commit()

# adds game 2
game2 = Game(name='Couter Strike', category='Shooting', created_by=1, is_active='1', is_delete='0')
session.add(game2)
session.commit()