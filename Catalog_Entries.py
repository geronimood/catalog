from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Catalog, CategoryItem, User

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
User1 = User(name="Master User", email="master_user@fakeemail.com",
             picture='/img/dummy_uswer.png')
session.add(User1)
session.commit()

# CategoryItems for Dallas Mavericks
catalog1 = Catalog(user_id=1, name="Dallas Mavericks")

session.add(catalog1)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Dirk Nowitzky", description="Best International Player Ever!",
                     catalog=catalog1)

session.add(categoryItem1)
session.commit()



print "added category items!"
