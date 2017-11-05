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

categoryItem1 = CategoryItem(user_id=1, name="Dirk Nowitzki", description="Best International Player Ever, earning MVP in 2007 and won the Championship in 2011",
                     catalog=catalog1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Steve Nash", description="Best Buddy of Dirk and a Great Point Guard, earning 2-times MVP!",
                     catalog=catalog1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Michael Finley", description="Great Player end of the 90s.",
                     catalog=catalog1)

session.add(categoryItem3)
session.commit()

# CategoryItems for LA Lakers
catalog2 = Catalog(user_id=1, name="Los Angeles Lakers")

session.add(catalog2)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Earving Magic Johnson", description="No Description needed - he was just MAGIC!!!",
                     catalog=catalog2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Kobey Bryant", description="20 Years at the same Team - what a Career!",
                     catalog=catalog2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Shaquille Rashaun O'Neal", description="A Beast in the Zone - and not a Beast from the Line",
                     catalog=catalog2)

session.add(categoryItem3)
session.commit()

# CategoryItems for Boston Celtics
catalog3 = Catalog(user_id=1, name="Boston Celtics")

session.add(catalog3)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Larry Bird", description="The Icon of the Celtics - for ever!",
                     catalog=catalog3)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Kyrie Irving", description="Possibly the Future of the Celtics - already won one Ring with LeBron...",
                     catalog=catalog3)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Isaiah Thomas", description="Unfortunately traded in 2017 - until then he was the Heart of the Celtics",
                     catalog=catalog3)

session.add(categoryItem3)
session.commit()

# CategoryItems for Chicago Bulls
catalog4 = Catalog(user_id=1, name="Chicago Bulls")

session.add(catalog4)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Michael Jordan", description="GOAT",
                     catalog=catalog4)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Scottie Pippen", description="Side by Side with Michael - he won everything and was the best Defender of the League!",
                     catalog=catalog4)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Dennis Rodman", description="Sometimes you need a Crazy Person to win it all...",
                     catalog=catalog4)

session.add(categoryItem3)
session.commit()

# CategoryItems for Utah Jazz
catalog5 = Catalog(user_id=1, name="Utah Jazz")

session.add(catalog5)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="John Stockton", description="One Part of Stockalone - and one of the greatest Guards ever.",
                     catalog=catalog5)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Carl Malone", description="The Mailman delivered every year - unfortunately there were the Bulls, too.",
                     catalog=catalog5)

session.add(categoryItem2)
session.commit()


print "added category items!"
