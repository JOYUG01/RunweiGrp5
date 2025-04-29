# RunweiGrp5

To lauch this project follow the steps below

Download the repository

```
git clone https://github.com/JOYUG01/RunweiGrp5.git
```

For this to work, we need to add valid credentials for google forms API. Add credentials.json to the base directory (same level as manage.py) and update the file name of the credentials in views.py on line 110.

Create a virtual enviroment and install django

```
python3 -m venv venv
```

```
source venv/bin/activate
pip install django
pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

```
cd RunweiGrp5
python manage.py runserver
```
If all is well, the development server will be running at http://127.0.0.1:8000/
