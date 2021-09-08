# Api

There is a rest api available to create, read, update and delete qr codes, and other models. The routes are standard REST api urls, which allows for easy integration with other apps.

| path           | parameters | description                                                                                                |
| -------------- | ---------- | ---------------------------------------------------------------------------------------------------------- |
| `qrcodes/`     | int:id     | This is a standard REST endpoint for QrCodes, all rest routes are included                                 |
| `apihits/`     | int:id     | This is a ReadOnlyViewset, meaning you can only do read operations on the ApiHit model (GET + GET with id) |
| `departments/` | int:id     | This is a standard REST endpoint for Departments, all rest routes are included                             |
| `urls/`        | int:id     | This is a standard REST endpoint for LinkUrls, all rest routes are included                                |
| `openapi/`     | -          | This route contains the generated openapi schema, with more documentation on the api                       |

## Redirecting a user to the json api

For easy integration with internal applications, you can also be redirected to the REST api.

The following use case is an example of how this functionality can be used.

- When a citizen, or user who does not expect some functionality, scans the qr code with a random app on his phone, we want to show him the `basic_info` page. Here he can read about the object he just scanned, and maybe see who it belongs to.
- An internal user could be provided with a custom app on his phone, which reads the url, embedded in the qr code. The app then requests the url with the .json suffix, or the header `Content-Type: application/json`, this will return the api response for this specific qr code, instead of showing the basic information. This allows the app to find all data the qr code has embedded. When using authentication for the api, you are seperating internal and external users on a qr code.

## Customize settings for the api

The REST api settings can be completely customized according to your needs. You can use the official [django REST framework docs](https://www.django-rest-framework.org/api-guide/settings/) for implementing these settings.

Here is an example which adds authentication to the REST api, and disables the browsable api:

```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}
```
