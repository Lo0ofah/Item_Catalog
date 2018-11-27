# Item Catalog
Item Catalog is a project for Udacity Full stack Nanodegree course
It is about building  web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Technologies used
* Python
* HTML
* CSS
* OAuth
* Flask Framework
* Linux virtual machine

## System Setup Required
* Download and install [vagrant](https://www.vagrantup.com/)
* Download and install [virtualBox](https://www.virtualbox.org/)

## Virtual Machine Setup
* Clone [FSND VM](https://github.com/udacity/fullstack-nanodegree-vm) it contain the vagrant setup
* Open terminal and enter to the vagrant folder that you just clone it then run these command
 * vagrant up
 * vagrant ssh
 * cd /vagrant

## Run The Project
* Clone or download this project
* Add this project inside vagrant folder
* Open Virtual Machine
* To create the database run python catalog_database_setup.py
* To add data into the database run python catalog_data.py
* To run the python file python application.py
* open http://localhost:5000

##JSON Endpoints
Catalog JSON: /catalog/JSON - lists all categories in the app.
