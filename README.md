#  Dublin Bus Overview

The main objective of Dublin Bus application is to make the travel easy and informative. From the passenger point of view the journey travel time has always been one of the biggest concerns and having bus-arrival times, bus-stop details and the leap card information available on helps a commuter to arrange their travel plans, and select the most convenient route to travel and interchange. To make the experience easier
 and timesaving there is a feature where passengers can add their frequent routes and bus-stop as favourites to make it more readily accessible.
 
## Technologies
Before getting started please be familiar with the stack below. Additionally it is important to understand basic [Git](https://gist.github.com/blackfalcon/8428401) and [Github](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests) for smooth collaboration as a team.

- **Backend**
    - Django, Rest Framework, Djoser

## Project Setup

1. Fork or Clone this repository
2. Setup it locally

### Local Setup

- Create Project directory
- Then use: pip install virtualenv
- Use git clone to get the project
- Cd into your the cloned repo as such
-Create and fire up your virtual environment
- Use: virtualenv  venv -p python3
- Then : source venv/bin/activate for windows venv/Scripts/activate


## Adding dependencies

- Install the dependencies needed to run the app : pip install -r requirements.txt

## Starting Up

* For database connection `python manage.py makemigrations`
* For database connection `python manage.py makemigrations api`
* For database connection `python manage.py makemigrations userauth`
* For migrating `python manage.py migrate`
* For migrating `python manage.py migrate userauth`
* For migrating `python manage.py migrate api`

## Ruuning Up

* `python manage.py runserver`

### Backend
* We used Rest Framework
* For login and authentication we user Djoser service.
* Userauth is the application for all auth details
* api is the application where all other api are created
* We followed Restful API guidelines.
  
### Database Auth
user - `dublinbus`
password - `1qaz2wsx!`
        
### Production
- We used jenkins for auto deployment.
- Credential For Jenkins:
    * Username: `admin`
    * Password: `1qaz2wsx!`
When a pull request is merged to production, it will automatically be deployed to the production environment. You can view the build logs in (https://bitbucket.org/ucd-comp47360-team-18/django-rest-dublinbus/src/master/). After the build successfully completes, wait a few minutes for the changes to be reflected, and then access the production app at http://137.43.49.66/home


