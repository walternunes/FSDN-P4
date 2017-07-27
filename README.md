# FSDN-P4
This project is part of Full Stack Developer Nanodegree

### About
Project 4: Item Catalog

### Objective
Develop an application that provides a list of items within a variety of categories.
The application should provide an user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.
An API to get items information should be implemented

### How to run the project

* This project uses Python2

1-) Install and setup the virtual machine
* Install Virtual Box, [Download](https://www.virtualbox.org/wiki/Downloads)
* Install Vagrant, [Download](https://www.vagrantup.com/downloads.html)
* Clone the following repository: ```https://github.com/udacity/fullstack-nanodegree-vm.git``` and ```cd``` into the folder 
* Enter vagrant folder by typing ```cd vagrant```
* Run ```vagrant up```
* Wait to download all dependencies and setup.

2-) Clone project and download Python dependencies
* Clone my "Item Catalog" project ```https://github.com/walternunes/FSDN-P4.git``` project in ```/vagrant/catalog``` folder
* Inside ```vagrant``` folder run ```vagrant ssh``` to access the machine (if you are not logged in yet)
* Download the python dependencies: ```pip install requests``` and ```pip install flask_wtf```

3-) Running the python and the project
* Type ```cd /vagrant``` to access the common folder
* Run ```python database_setup.py``` to configure database model
* Run ```python catalog_data.py``` to load initial database data
* Run ```python catalog.py```
* In your browser access ```localhost:5000```

### API endpoints
* /api/v1/catalog/ - Get all items registered 
* /api/v1/categories/ - Get all categories registered
* /api/v1/catalog/<int:catalog_id>/items - Get all items of the requested catalog(category)
* /api/v1/catalog/<int:catalog_id>/item/<int:item_id> - Get item detail of the requested item
