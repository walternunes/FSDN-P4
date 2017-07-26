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
             picture="")
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


category9 = Category(name="Skate")

session.add(category9)
session.commit()


category10 = Category(name="Surf")

session.add(category10)
session.commit()


# Items
# Catalog Items of category Snowboard
catalogItem1 = CatalogItem(name="Snowboard", description="Best for any terrain and conditions. All-mountain snowboards perform anywhere on a mountain-groomed runs, backcountry, even park and pipe. They may be directional or twin-tip. Most boardes ride all-mountain boards.",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(name="Snowboard boots", description="Extremely versatile and smooth for a comfortable ride all over the mountain. A dual-zone Boa Lacing system is hassle-free and easy to adjust combined with versatile fit and flex you can count on ",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem2)
session.commit()


catalogItem3 = CatalogItem(name="Goggles", description="Designed specifically to accommodate your spectacles as they simultaneously shield your face from the pelting sting of snow and/or harsh rays. A stronger Super Anti-Fog coating, on-trend cylindrical lenses,",
                     image_url="", category=category1, user_id=1)

session.add(catalogItem3)
session.commit()

# Catalog Items of category Hockey
catalogItem4 = CatalogItem(name="Helmet", description=" A helmet with strap, and optionally a face cage or visor, is required of all ice hockey players. Hockey helmets come in various sizes, and many of the older designs can also be adjusted by loosening or fastening screws at the side or at the back. Ice hockey helmets are made of a rigid but flexible thermoplastic outer shell, usually nylon or ABS, with firm vinyl nitrile foam padding inside to reduce shocks. Even with the helmet and visor/face cage, concussions and facial injuries are common injuries in the sport.",
                     image_url="", category=category2, user_id=1)

session.add(catalogItem4)
session.commit()


catalogItem5 = CatalogItem(name="Puck", description=" 3 inch diameter, 1 inch thick, 6 ounces (170 g) vulcanized rubber disk. The control of this object will determine the outcome of the game.",
                     image_url="", category=category2, user_id=1)

session.add(catalogItem5)
session.commit()


catalogItem6 = CatalogItem(name="Stick", description="Made of wood or composite materials, hockey sticks come in various styles and lengths. Stick dimensions vary based on the size of the player. Traditionally, all sticks were wooden up until the late 1990s; wood is inexpensive and tough, but the characteristics of each stick will be subtly different due to small changes in the grain structure",
                     image_url="", category=category2, user_id=1)

session.add(catalogItem6)
session.commit()


# Catalog Items of category Soccer
catalogItem7 = CatalogItem(name="Soccer Ball", description="Soccer ball",
                     image_url="", category=category3, user_id=1)

session.add(catalogItem7)
session.commit()


catalogItem8 = CatalogItem(name="Gloves", description="The gloves have a close fit secured by a seamless bandage around the wrist. Gloves promote a firm handle on the ball ",
                     image_url="", category=category3, user_id=1)

session.add(catalogItem8)
session.commit()


catalogItem9 = CatalogItem(name="Soccer Shin", description="Soccer shin guards are designed to protect you from 50-50 challenges and tackles as you dribble around defenders",
                     image_url="", category=category3, user_id=1)

session.add(catalogItem9)
session.commit()


# Catalog Items of category Tennis
catalogItem10 = CatalogItem(name="Tennis ball", description="Green tennis ball",
                     image_url="", category=category4, user_id=1)

session.add(catalogItem10)
session.commit()


catalogItem11 = CatalogItem(name="Racket", description="The components of a tennis racket include a handle, known as the grip, connected to a neck which joins a roughly elliptical frame that holds a matrix of tightly pulled strings",
                     image_url="", category=category4, user_id=1)

session.add(catalogItem11)
session.commit()


# Catalog Items of category Golf
catalogItem12 = CatalogItem(name="Golf Ball", description="A small golf ball",
                     image_url="", category=category5, user_id=1)

session.add(catalogItem12)
session.commit()


catalogItem13 = CatalogItem(name="Golf Club", description="There are three major types of clubs, known as woods, irons, and putters. Woods are played for long shots from the tee or fairway, and occasionally rough, while irons are for precision shots from fairways as well as from the rough",
                     image_url="", category=category5, user_id=1)

session.add(catalogItem13)
session.commit()


catalogItem14 = CatalogItem(name="Tee", description="A tee is an object (wooden or plastic) that is pushed into or placed on the ground to rest a ball on top of for an easier shot; however, this is only allowed for the first stroke (tee shot or drive) of each hole",
                     image_url="", category=category5, user_id=1)

session.add(catalogItem14)
session.commit()


# Catalog Items of category Basketball
catalogItem15 = CatalogItem(name="BasketBall ball", description="A basketball ball",
                     image_url="", category=category6, user_id=1)

session.add(catalogItem15)
session.commit()


catalogItem16 = CatalogItem(name="hoop", description="Horizontal circular metal hoop supporting a net through which players try to throw the basketball",
                     image_url="", category=category6, user_id=1)

session.add(catalogItem16)
session.commit()



# Catalog Items of category Volleyball
catalogItem17 = CatalogItem(name="Volleyball Ball", description="A volleyball ball",
                     image_url="", category=category7, user_id=1)

session.add(catalogItem17)
session.commit()


catalogItem18 = CatalogItem(name="Net", description="The net divides the volleyball court into two halves. ",
                     image_url="", category=category7, user_id=1)

session.add(catalogItem18)
session.commit()



# Catalog Items of category Skii
catalogItem19 = CatalogItem(name="Snowboard", description="Best for any terrain and conditions. Perform spins anywhere on a mountain-groomed runs, backcountry, even park and pipe. They may be directional or twin-tip. Most boardes ride all-mountain boards.",
                     image_url="", category=category8, user_id=1)

session.add(catalogItem19)
session.commit()

catalogItem20 = CatalogItem(name="Skii Poles", description="Strong, lightweight, and equipped with an interchangeable basket system. Your Poles simply get 'er done.",
                     image_url="", category=category8, user_id=1)

session.add(catalogItem20)
session.commit()


catalogItem20 = CatalogItem(name="Skii Boots", description="Extremely versatile and smooth for a comfortable ride all over the mountain. A dual-zone Boa Lacing system is hassle-free and easy to adjust combined with versatile fit and flex you can count on ",
                     image_url="", category=category8, user_id=1)

session.add(catalogItem20)
session.commit()


# Catalog Items of category Skate
catalogItem21 = CatalogItem(name="Trucks", description="Ready to be thrashed and thunderstruck day in and day out, enough for curb bashes and years of grinds on gritty surfaces.",
                     image_url="", category=category9, user_id=1)

session.add(catalogItem21)
session.commit()


catalogItem22 = CatalogItem(name="Deck", description=" Skateboard Deck  that lets you wherever you want, two trucks, and four wheels might take you.",
                     image_url="", category=category9, user_id=1)

session.add(catalogItem22)
session.commit()


catalogItem23 = CatalogItem(name="Wheels", description="Get your Wheels and hit the streets.",
                     image_url="", category=category9, user_id=1)

session.add(catalogItem23)
session.commit()


# Catalog Items of category Surf
catalogItem24 = CatalogItem(name="Surfboard", description="A versatile board that will perform regardless of the swell's sometimes stubborn style. Proper for hold speed while still responsive enough to whip up and hit the lip.",
                     image_url="", category=category10, user_id=1)

session.add(catalogItem24)
session.commit()


catalogItem25 = CatalogItem(name="Wetsuits", description="NeoPrene, Glued and blindstitched seams are fully taped with Thermo Dry seam tape for added penetration protection and a well thought out Water Barrier Inner Dam between the zipper and your back all but eliminates common qualms with rear-entry wetsuits.",
                     image_url="", category=category10, user_id=1)

session.add(catalogItem25)
session.commit()


catalogItem26 = CatalogItem(name="Board bag", description="Padded rail protection, an ergonomic shoulder pad, long-life marine zippers and much more, this bag is suited to treat your board with care.",
                     image_url="", category=category10, user_id=1)

session.add(catalogItem26)
session.commit()
