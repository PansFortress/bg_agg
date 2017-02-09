import os, requests
import xml.etree.ElementTree as ET
import time
from flask_script import Manager
from bg_agg import app
from bg_agg.database import Base, session
from bg_agg.models import Review, Product, Reviewer

manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

@manager.command
def addreviewer():
    display_name = input("Display Name: ")
    critic = False
    reviewer = Reviewer(display_name=display_name, critic=critic)
    session.add(reviewer)
    session.commit()
    
@manager.command
def gettopfifty():
    try:
        r = requests.get("https://www.boardgamegeek.com/xmlapi2/hot?type=boardgame")

        if not r.status_code == 200:
            return "Error: Unexpected response {}".format(r)

        root = ET.fromstring(r.text)
        createProducts(root)

        products = session.query(Product).filter(Product.name == None).limit(2).all()
        for product in products:
            try:
                time.sleep(1)
                r = requests.get("https://www.videogamegeek.com/xmlapi2/thing?id={}&comments=1".format(product.e_id))
                if not r.status_code == 200:
                    return "Error: Unexected response with {}".format(r)

                root = ET.fromstring(r.text)
                populateProduct(product, root)

            except requests.exceptions.RequestException as e:
                print("Sleeping for 60 seconds due to {}".format(e))
                time.sleep(60)
    
    except requests.exceptions.RequestException as e:
        return "Error: {}".format(e)

def createProducts(root):
    for item in root.iter('item'):
        product = session.query(Product).filter(Product.e_id == item.attrib["id"]).first()
        if not product:
            product = Product(e_id = item.attrib["id"])
            session.add(product)
            session.commit()

def populateProduct(product, root):
    for item in root.iter('description'):
        # print(item.text)
        pass
    for item in root.iter('name'):
        if(item.attrib["type"] == "primary"):
            # print(item.attrib["value"])
            pass

    first=True
    for item in root.iter('link'):
        if(item.attrib["type"] == "boardgamepublisher" and first):
            # print(item.attrib["value"])
            first = False

    for item in root.iter('yearpublished'):
        # print(item.attrib["value"])
        pass

    players = ''
    for item in root.iter('minplayers'):
        players += item.attrib["value"]
        players += " - "
    for item in root.iter('maxplayers'):
        players += item.attrib["value"]
    # print(players)

    for item in root.iter('image'):
        print("http:{}".format(item.text))

if __name__ == "__main__":
    manager.run()