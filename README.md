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
	* `create database project;`
	* `create user project with password 'project';`
	* `alter database project owner to project;`
* Deployment
	* `python manage.py runserver 0.0.0.0:8080`

## Development

* Comments
	* Comments at the head of each file
		* File name, description
	* Comments for functions
		* Parameter(s), return value(s), description
	* Style
		* One space after the # sign for comments in python
		* No spaces between hyphens and the comment in html  <!--[comment]-->
		* Defining variable usage should be on the same line, separated by a space
* Syntax
	* Import in alphabetical order
	* Tab size of 2
	* One blank line at the end of each file
	* CSS
		* One space after the colon
		* One tab in the body
	* Capitalization
		* Non-django classes/variables should be defined with underscores (not camel-case)
		* Classes should have the first letter capitalized
		* Objects, variables, and functions should be all lowercase
	* Spacing
		* Separate classes with two newlines
		* Separate functions with one newlines
		* Mathematical operators should have a space on both ends
		* No space before or after parenthesis
		* One space after a comma
* Git
	* `git rebase` when merging to remove merge commits
	* Format of commits:
		* *Capitalize* first letter in both parts
		`Short description: Longer description`
	* Keep commits between 20 and 200 lines
* README
	* Add any added dependencies to the README
	* Update with changed configurations
	* Commit format:
	`README.md: Short description`
