from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///categories.db')
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

# Create user
User1 = User(name="Elaaf zaker", email="Elaaf@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

ctegory1 = Category(name="acer")
session.add(ctegory1)
session.commit()

item1_1 = Item(user_id=1, name="Swift 3", description="Laptop with a hard drive of 128 GB and a 4 SDRAM RAM.", category=ctegory1)
session.add(item1_1)
session.commit()

item1_2 = Item(user_id=1, name="Switch 3", description="Perfect blend of a laptop and tablet with modes to fit into every situation.", category=ctegory1)
session.add(item1_2)
session.commit()
#--------------------------------------------------------------
ctegory2 = Category(name="ASUS")
session.add(ctegory2)
session.commit()

item2_1 = Item(user_id=1, name="ZenFone 5", description="Quad cameras: 20MP + 8MP Wide-angle Front Cameras / 16MP, Dual Nano SIM slots and MicroSD Card Slot (up to 2TB), Compatible with GSM Networks including AT&T, T-Mobile, Straight Talk, Walmart Family.", category=ctegory2)
session.add(item2_1)
session.commit()

item2_2 = Item(user_id=1, name="VivoBook Pro", description="Powerful 8th Generation Intel Core i7-8750H Standard Voltage Processor, NVIDIA GTX 1050 4GB discrete graphics with ASUS Hyper Cool, dual-copper and dual-fan, 15.6 FHD WideView IPS level Panel with ASUS Splendid enhancements, 8GB DDR4 RAM + 16GB Intel Optane Memory.", category=ctegory2)
session.add(item2_2)
session.commit()

item2_3 = Item(user_id=1, name="ROG Spotlight", description="RGB Logo Projector in Matte Black with Aura Sync Lighting Software, 360-Degree Rotation using the coin screw aligns the ROG Eye, Project Distance Up to 40 allows you flexibility in placing the Spotlight.", category=ctegory2)
session.add(item2_3)
session.commit()
#--------------------------------------------------------
ctegory3 = Category(name="TOSHIBA")
session.add(ctegory3)
session.commit()

item3_1 = Item(user_id=1, name="Tecra A40-C1443", description="Intel Core i5-6200U Processor, MEMORY 8 GB DDR3L 1600 MHz, HARD DRIVE 256 GB M.2 Solid State Drive (SSD), OPTICAL DRIVE DVD SuperMulti drive supporting 11 formats.", category=ctegory3)
session.add(item3_1)
session.commit()
#----------------------------------------------------------
ctegory4 = Category(name="Apple")
session.add(ctegory4)
session.commit()

item4_1 = Item(user_id=1, name="iPhone 7", description="smartphone was launched in September 2016. The phone comes with a 4.70-inch touchscreen display with a resolution of 750 pixels by 1334 pixels at a PPI of 326 pixels per inch. Apple iPhone 7 price in India starts from Rs. 33,149.", category=ctegory4)
session.add(item4_1)
session.commit()
#----------------------------------------------------------
ctegory5 = Category(name="HP")
session.add(ctegory5)
session.commit()

item5_1 = Item(user_id=1, name="Sprocket", description="Photo Printer, Print photos from your smartphone or tablet as easily as you post them. Instantly share 2 x 3-inch (5 x 7.6 cm) snapshots or stickers of every fun-filled moment.", category=ctegory5)
session.add(item5_1)
session.commit()

print "added items!"
