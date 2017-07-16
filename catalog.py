from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem
app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all restaurants
@app.route('/')
@app.route('/catalog/')
def showCategory():
    categories = session.query(Category).all()
    # return "This page will show all my categories"
    return render_template('index.html', categories=categories)

@app.route('/catalog/<int:catalog_id>')
@app.route('/catalog/<int:catalog_id>/items')
def detailCategory(catalog_id):
	# Get all categories
	categories = session.query(Category).all()


	category = session.query(Category).filter_by(id = catalog_id).first()
	categoryName = category.name
	categoryItems = session.query(CatalogItem).filter_by(category_id = catalog_id).all()
	test = 1;
	return render_template('index.html', categories = categories, categoryItems = categoryItems, categoryName = categoryName, test = test)

@app.route('/catalog2/<int:catalog_id>')
@app.route('/catalog2/<int:catalog_id>/items')
def detailCategory2(catalog_id):
	# Get all categories
	categories = session.query(Category).all()


	category = session.query(Category).filter_by(id = catalog_id).first()
	categoryName = category.name
	categoryItems = session.query(CatalogItem).filter_by(category_id = catalog_id).all()
	test2 = 1;
	return render_template('index.html', categories = categories, categoryItems = categoryItems, categoryName = categoryName, test2 = test2)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)