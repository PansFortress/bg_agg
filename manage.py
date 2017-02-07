import os
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
    
if __name__ == "__main__":
    manager.run()