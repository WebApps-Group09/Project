# Podlife

## Summary

* CSE 40613 - Web Applications Development
* Podlife is a podcast hosting web service, where users can upload their own podcasts and review the ones currently on the site. Most of the podcasts that are popular today are series; our goal is	to create a place where anyone can share single episodes that can be categorized for specific interests.

## Contributors

* Group09
	* Ann Keenan (akeenan2)
	* Catherine Badart (cbadart)
	* Luke Duane (lduane)
	* Michael Sills (msills)

## Technology

* Server `group09.dhcp.nd.edu`, IP address `10.173.153.179`
* Backend:
	* Django
	* Postgres, SQL
* Frontend:
	* javascript, jquery
	* HTML, Django templating
	* CSS, bootstrap

## Set Up

* Configuration
	* `virtualenv -p python3.5 venv`
	* `source venv/bin/activate`
* Dependencies
	* `pip install pip install Django==1.11.6 psycopg2==2.7.3.2`
* Database
	* `create database podlife;`
	* `create user group09 with password 'project';`
	* `alter database podlife owner to project;`
* Deployment
	* `python manage.py runserver 0.0.0.0:8080`
