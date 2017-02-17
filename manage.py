import os, requests
import xml.etree.ElementTree as ET
import time
from faker import Faker
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash
from bg_agg import app
from bg_agg.database import Base, session
from bg_agg.models import Review, Product, Reviewer

# TODO: Need to add logging to the seeding process to confirm where we fail

fake = Faker()
manager = Manager(app)

@manager.command
def addreviewer():
    display_name = input("Display Name: ")
    critic = True
    password = input("Password: ")
    reviewer = Reviewer(display_name=display_name, critic=critic,
                        password=generate_password_hash(password))
    session.add(reviewer)
    session.commit()
    
def createProducts(root):
    for item in root.iter('item'):
        product = session.query(Product).filter(Product.e_id == item.attrib["id"]).first()
        # Blacklist 193738 due to encoding issues with XML data back. BGG API sent back
        # 200 status_code while reporting an error in messaging for this
        if not product and item.attrib["id"] != "193738":
            product = Product(e_id = item.attrib["id"])
            session.add(product)
            session.commit()

@manager.command
def gettopfifty():
    try:
        r = requests.get("https://www.boardgamegeek.com/xmlapi2/hot?type=boardgame")

        if not r.status_code == 200:
            return "Error: Unexpected response {}".format(r)

        root = ET.fromstring(r.text)
        createProducts(root)
    
    except requests.exceptions.RequestException as e:
        return "Error: {}".format(e)

#TODO: Make a function to check for first instance of a key in the tree while also
# giving the ability to filter
def populateProduct(product, root):
    for item in root.iter('description'):
        product.description = item.text
    for item in root.iter('name'):
        if(item.attrib["type"] == "primary"):
            product.name = item.attrib["value"]

    for item in root.iter('link'):
        if(item.attrib["type"] == "boardgamepublisher" and not product.publisher):
            product.publisher = item.attrib["value"]

    for item in root.iter('yearpublished'):
        product.release = item.attrib["value"]

    # Only expect to iterate over each loop once as we only expect one minplayers and
    # one maxplayers returned in the XML document
    players = ''
    for item in root.iter('minplayers'):
        players += item.attrib["value"]
    players += " - "
    for item in root.iter('maxplayers'):
        players += item.attrib["value"]
    product.player_num = players

    for item in root.iter('image'):
        product.image = "http:{}".format(item.text)
    
    session.commit()

def populateReviews(product, root):
    for item in root.iter('comment'):
        if item.attrib["rating"] != "N/A":
            user = getUser(item.attrib["username"])

            review = session.query(Review).filter(Review.reviewer == user).filter(Review.product == product).first()
            if review is None:
                review = Review(raw_score=item.attrib["rating"],
                                score=tenToScore(item.attrib["rating"]),
                                summary=item.attrib["value"][:140],
                                review=item.attrib["value"][:1500],
                                source="https://boardgamegeek.com/boardgame/{}/{}/ratings".\
                                format(product.e_id, product.name),
                                product=product,
                                reviewer=user)
                session.add(review)
                session.commit()

def getUser(username):
    user = session.query(Reviewer).filter(Reviewer.display_name == username).first()
    if user:
        return user

    user = Reviewer(display_name=username, 
                    critic=False,
                    password='')
    session.add(user)
    session.commit()
    return user

@manager.command
def seedmissing():
    products = session.query(Product).filter(Product.description == None).all()
    for product in products:
        try:
            time.sleep(1)
            r = requests.get("https://www.videogamegeek.com/xmlapi2/thing?id={}&comments=1".format(product.e_id))
            if not r.status_code == 200:
                return "Error: Unexected response with {}".format(r)

            root = ET.fromstring(r.text)
            populateProduct(product, root)
            populateReviews(product, root)

        except requests.exceptions.RequestException as e:
            print("Sleeping for 60 seconds due to {}".format(e))
            time.sleep(60)
        except ET.ParseError:
            print("{} is corrupt".format(r.text))

@manager.command
def seedPasswords(defaultPassword):
    users = session.query(Reviewer).filter(Reviewer.password == '').all()
    for user in users:
        user.password = generate_password_hash(defaultPassword)
    session.commit()

@manager.command
def seedImages():
    products = session.query(Product).filter(Product.image == None).all()
    for product in products:
        product.image = "http://tincan.co.uk/sites/default/files/banners/tc-404.jpg"
    session.commit()

@manager.command
def seedCriticReviews():
    products = session.query(Product).all()
    shutupandsitdown = session.query(Reviewer).filter(Reviewer.display_name == "shutupandsitdown").first()
    dicetowerreviews = session.query(Reviewer).filter(Reviewer.display_name == "dicetowerreviews").first()
    eightoclock = session.query(Reviewer).filter(Reviewer.display_name == "eightoclock").first()
    negativenate = session.query(Reviewer).filter(Reviewer.display_name == "negativenate").first()

    for product in products:
        review10 = Review(raw_score=10,
                                score=tenToScore(10),
                                summary="This was an amazing game, never forget {}".format(fake.sentences(nb=1)[0]),
                                review="This was an amazing game, never forget {}".format(fake.sentences(nb=1)[0]),
                                product=product,
                                reviewer=shutupandsitdown)

        review8 = Review(raw_score=8,
                                score=tenToScore(8),
                                summary="This was a great amazing game, could be better {}".format(fake.sentences(nb=1)[0]),
                                review="This was a somewhat an amazing game, could be better {}".format(fake.sentences(nb=1)[0]),
                                product=product,
                                reviewer=eightoclock)

        review5 = Review(raw_score=5,
                                score=tenToScore(5),
                                summary="This was a somewhat disappointing game, could be better {}".format(fake.sentences(nb=1)[0]),
                                review="This was a somewhat disappointing game, could be better {}".format(fake.sentences(nb=1)[0]),
                                product=product,
                                reviewer=dicetowerreviews)

        review1 = Review(raw_score=1,
                                score=tenToScore(1),
                                summary="This was a terrible game, do not purchase {}".format(fake.sentences(nb=1)[0]),
                                review="This was a terrible game, do not purchase {}".format(fake.sentences(nb=1)[0]),
                                product=product,
                                reviewer=negativenate)

        session.add_all([review10, review5, review1])
        session.commit()

def tenToScore(val):
    return float(val)/2

def textToScore(val):
    if val == "buy":
        return 4.0
    else:
        return 2.0

class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

migrate = Migrate(app, DB(Base.metadata))
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()