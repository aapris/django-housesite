# django-housesite

A bunch of Django applications to implement a home site for 
homeowner associations.

Requirements
============

* PostgreSQL + PostGIS (though no reason for that yet)
* Python >3.4

Setup
=====

```
cd housesite/settings/
cp local.py.example local.py
vim local.py  # set DATABASE
createdb YOUR_DATABASENAME  # same as in local.py
cd ../..
python manage.py migrate
python manage.py createsuperuser
```

* Go to /admin/
* Navigate to Explorer --> Welcome to your new Wagtail site!
* Create a new subpage (type Home Page) and then move this page into 'Root'.
* Go to Settings -> Sites and change Root page

