# QR-Toolkit Core package

## Documentation

* [Full documentation](https://qr-toolkit-core.readthedocs.io/en/latest/)
* [Example repository](https://github.com/lab9k/qr-toolkit-core-example)


## Installation

```shell
python3 -m pip install django-qr-toolkit-core
```

## usage

1. Add the package to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... your other apps
    'qrtoolkit_core'
]
```

2. Add the following settings

```python
API_URL = '/api/'  # Url to the api endpoint (change this if you are setting up api and public redirect service seperatly)
REDIRECT_SERVICE_URL = ''  # Url to the redirect service endpoint (change this if you are setting up api and public redirect service seperatly)
ENVIRONMENT = 'DV'  # Env the service is deployed in. (DV,QA,PR, etc)
```

3. urls.py setup

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

### The following paths will be installed:

`code_routes`

| path | parameters | description | 
| --- | --- | --- |
| `<slug:short_uuid>/` | slug (uuid or short_uuid of a QrCode) | This is the route that will take care of routing a user (on scan) |
| `<slug:short_uuid>.[json/html]/` | same as route above | This is the same route as the above route, but suffixed with .html or .json. .html will return the same as above, while .json will redirect to the API_URL setting |
| `call/<int:pk>/` | LinkUrl id | This is the route which is called when the user selects a url in Kiosk mode |

`api_routes`

| path | parameters | description | 
| --- | --- | --- |
| `qrcodes/` | int:id | This is a standard REST endpoint for QrCodes, all rest routes are included |
| `apihits/` | int:id | This is a ReadOnlyViewset, meaning you can only do read operations on the ApiHit model (GET + GET with id) |
| `departments/` | int:id | This is a standard REST endpoint for Departments, all rest routes are included |
| `urls/` | int:id | This is a standard REST endpoint for LinkUrls, all rest routes are included |
| `openapi/` | - | This route contains the generated openapi schema, with more documentation on the api | 
