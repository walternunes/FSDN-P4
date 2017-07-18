from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem

engine = create_engine('sqlite:///itemcatalog.db')
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


# Menu for Category
category1 = Category(name="Snowboarding")

session.add(category1)
session.commit()

catalogItem1 = CatalogItem(name="Snowboard", description="Snowboard description",
                     image_url="", category=category1)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(name="Goggles", description="A pair of goggles",
                     image_url="", category=category1)

session.add(catalogItem2)
session.commit()



category2 = Category(name="Hockey")

session.add(category2)
session.commit()


catalogItem3 = CatalogItem(name="Stick", description="Quality stick",
                     image_url="", category=category2)

session.add(catalogItem3)
session.commit()