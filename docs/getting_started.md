# Getting Started

## Requirements

### Local machine

assuming you are developing on a local machine, you should have set up a virtual python environment. You can do this with the command below

```shell
python3 -m venv venv
```

You can then activate the environment in the current shell with the following command.

```shell
source ./venv/bin/activate
```

Detailed instructions on how to activate the virtual environment on different OS's are found [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

### Installing the qr toolkit

```shell
# Install the qr-toolkit-core package
python3 -m pip install django-qr-toolkit-core

# Scaffold your Django project
django-admin startproject myqrtoolkit .
```

## Usage

### settings

- Add the qr toolkit app to your INSTALLED_APPS setting

```python
INSTALLED_APPS = [
    # ... your other apps
    'reversion',  # Adds history to certain models
    'django_filters',  # This adds filters to the rest api
    'rest_framework',  # This will enable the api
    'qrtoolkit_core'
]
```

- Add the following required settings

```python
API_URL = '/api/'
REDIRECT_SERVICE_URL = ''
ENVIRONMENT = 'DV'
```

`API_URL`: Url to the api endpoint (change this if you are setting up api and public redirect service seperatly, if not, you can just leave this)

`REDIRECT_SERVICE_URL`: Url to the redirect service endpoint (change this if you are setting up api and public redirect service seperatly)

`ENVIRONMENT`: Env the service is deployed in. (DV,QA,PR, etc)

### urls.py

```python
from django.contrib import admin
from django.urls import path, include
from qrtoolkit_core import urls as qr_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(qr_urls.api_routes)),
    path('', include(qr_urls.code_routes))
]
```

The code routes and api routes are split up, so that you can deploy the api and public service seperatly, and optionally
deploy the api behind an api gateway. The api does not do authentication by default, but can also be configured
with [django-rest-framework settings](https://www.django-rest-framework.org/api-guide/settings/).

If you include the admin urls, the qrtoolkit models will automatically appear in the admin dashboard

- The following paths will be installed:

`code_routes`

| path                             | parameters                            | description                                                                                                                                                        |
| -------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `<slug:short_uuid>/`             | slug (uuid or short_uuid of a QrCode) | This is the route that will take care of routing a user (on scan)                                                                                                  |
| `<slug:short_uuid>.[json/html]/` | same as route above                   | This is the same route as the above route, but suffixed with .html or .json. .html will return the same as above, while .json will redirect to the API_URL setting |
| `call/<int:pk>/`                 | LinkUrl id                            | This is the route which is called when the user selects a url in Kiosk mode                                                                                        |

`api_routes`

More information on the api routes is available in the [api docs](api.md)

### Migrations and superuser

After all these steps you want to create the local database (sqlite by default), run the migrations the qrtoolkit provides, and create a superuser, so you can login locally

```shell
python manage.py migrate

python manage.py createsuperuser # This command will propt you for input
```

### Running the server

You can start the development server by issuing the following command

```shell
python manage.py runserver
```

When this command is running, you can navigate your browser to localhost:8000/admin , which will let you log in with the credentials you provided above (the superuser you created)

### Creating a custom app

You can create your own app, with your own models, which you can then link to specific qr codes.

#### Scaffold the app

```shell
python manage.py startapp mycustomapp
```

#### Add the app to settings.py

in settings.py, add your app to INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'qrtoolkit_core',
    'mycustomapp'  # Make sure this is after qrtoolkit_core for customization to behave correctly
]
```

#### Add a model

in the file `mycustomapp/models.py` you can setup your own models.
e.g. :

```python
from django.db import models
from django.contrib.auth import get_user_model
from qrtoolkit_core import models as qr_models


class MyObject(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='user_objects')

    qrcode = models.OneToOneField(to=qr_models.QRCode, related_name='myobject', on_delete=models.CASCADE)

```

#### create migrations for your model

```shell
python manage.py makemigrations
python manage.py migrate # This command will run the created migrations, and update your local database
```

#### Add your model to the django admin

in the file `mycustomapp/admin.py` add the following

```python
from django.contrib import admin
from mycustomapp.models import MyObject

@admin.register(MyObject)
class MyObjectAdmin(admin.ModelAdmin):
    pass
```

That's it! You now have access to your custom model in the django admin dashboard.
