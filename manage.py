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

        tree = ET.fromstring(r.text)

        # topfifty_ids = []
        count = 0
        for child in tree:
            try: 
                time.sleep(1)
                r = requests.get("https://www.videogamegeek.com/xmlapi2/thing?id={}&comments=1".format(child.attrib["id"]))
                if not r.status_code == 200:
                    return "Error: Unexpected response {}".format(r)

                child_tree = ET.fromstring(r.text)
                count += 1
                for item in child_tree:
                    for i in item:
                        if i.tag == "name" and i.attrib["type"] == "primary":
                            print(str(count) + " : " + i.attrib["value"])
            except requests.exceptions.RequestException as e:
                print("Sleeping for 60 seconds due to {}".format(e))
                time.sleep(60)

            # _tree = ET.fromstring(r.text)
            # for item in _tree:
            #     for i in item:
            #         time.sleep(1)
            #         if i.tag == "name" and i.attrib["type"] == "primary":
            #             print(i.attrib["value"])
        

    except requests.exceptions.RequestException as e:
        return "Error: {}".format(e)

if __name__ == "__main__":
    manager.run()