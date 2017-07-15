from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category
app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all restaurants
@app.route('/')
@app.route('/catalog/')
def showRestaurants():
    categories = session.query(Category).all()
    # return "This page will show all my categories"
    return render_template('categories.html', categories=categories)




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)