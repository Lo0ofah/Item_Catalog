from flask import Flask, render_template, request, redirect, url_for, flash , jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Category, Item, User

app = Flask(__name__)

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(Item.id.desc()).limit(5)
    return render_template('catalog.html', categories = categories, latestItems = latestItems)

@app.route('/catalog/<string:category_name>/items')
def categoryItems(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    return render_template('categoryItems.html', categories = categories, category = category, items = items)

@app.route('/catalog/<string:category_name>/<string:item_name>')
def itemDescription(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    return render_template('itemDescription.html', item = item)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
