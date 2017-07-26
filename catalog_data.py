from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem, User

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


# Create dummy user
user1 = User(name="Admin", email="admin@admin.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()


# Category
category1 = Category(name="Snowboarding")

session.add(category1)
session.commit()


category2 = Category(name="Hockey")

session.add(category2)
session.commit()


category3 = Category(name="Soccer")

session.add(category3)
session.commit()


category4 = Category(name="Tennis")

session.add(category4)
session.commit()


category5 = Category(name="Golf")

session.add(category5)
session.commit()


category6 = Category(name="Basketball")

session.add(category6)
session.commit()


category7 = Category(name="Volleyball")

session.add(category7)
session.commit()


category8 = Category(name="Skiing")

session.add(category8)
session.commit()


category9 = Category(name="Judo")

session.add(category9)
session.commit()


category10 = Category(name="Surf")

session.add(category10)
session.commit()


# Items
catalogItem1 = CatalogItem(name="Snowboard", description="Snowboard description",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem1)
session.commit()


catalogItem1 = CatalogItem(name="Snowboard boots", description="snowboard boots ",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(name="Goggles", description="A pair of goggles",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem2)
session.commit()


catalogItem3 = CatalogItem(name="Stick", description="Quality stick",
                     image_url="", category=category2, user_id=1)

session.add(catalogItem3)
session.commit()