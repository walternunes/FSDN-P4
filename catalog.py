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
	categoryId = category.id
	categoryItems = session.query(CatalogItem).filter_by(category_id = catalog_id).all()
	test = 1;
	return render_template('index.html', categories = categories, categoryItems = categoryItems, categoryName = categoryName, categoryId = categoryId, test = test)

	
@app.route('/catalog/<int:catalog_id>/item/<int:item_id>')
def detailItem(catalog_id, item_id):
	catalogItem = session.query(CatalogItem).filter_by(id = item_id).first()

	return render_template('detail_item.html', catalog_id=catalog_id, catalogItem = catalogItem)

@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
def editItem(catalog_id, item_id):
    editedItem = session.query(CatalogItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['image_url']:
            editedItem.image_url = request.form['image_url']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('detailItem', catalog_id=catalog_id, item_id=item_id))
    else:
        return render_template(
            'edit_item.html', catalog_id=catalog_id, item_id=item_id, item=editedItem)

@app.route(
    '/catalog/item/create',
    methods=['GET', 'POST'])
def createItem():
	# Get all categories
	categories = session.query(Category).all()
	if request.method == 'POST':
		newItem = CatalogItem(
		name=request.form['name'],
			description=request.form['description'],
			image_url=request.form['image_url'],
			category_id=request.form['category'])
		session.add(newItem)
		session.commit()

		return redirect(url_for('showCategory'))
	else:
		return render_template('create_item.html', categories=categories)


@app.route('/catalog/<int:catalog_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(catalog_id, item_id):
    itemToDelete = session.query(CatalogItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('delete_item.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id
	

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)