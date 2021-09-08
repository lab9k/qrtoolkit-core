# Models

## QRCode

| field        | type                                        | description                                                                                 |
| ------------ | ------------------------------------------- | ------------------------------------------------------------------------------------------- |
| title        | [CharField]({{docs_url}}#charfield)         | title of the qr code                                                                        |
| department   | [Department](#department)                   | can be used to seperate qr codes for different users,</br> also linking them to departments |
| uuid         | [UUIDField]({{docs_url}}#uuidfield)         | long identifier for the qr code (used in urls)                                              |
| short_uuid   | [SlugField]({{docs_url}}#slugfield)         | short identifier for the qr code (also used in urls)                                        |
| basic_info   | [TextField]({{docs_url}}#textfield)         | Basic info about the qr code. Can be filled in with any text                                |
| mode         | QRCode.REDIRECT_MODE_CHOICES                | The mode a qrcode is in. See [modes](./modes.md)                                            |
| created      | [DateTimeField]({{docs_url}}#datetimefield) | automatically created                                                                       |
| last_updated | [DateTimeField]({{docs_url}}#datetimefield) | automatically updated                                                                       |

## Department

| field | type                                | description                         |
| ----- | ----------------------------------- | ----------------------------------- |
| name  | [CharField]({{docs_url}}#charfield) | name of the department              |
| users | auth.User                           | users who belong in this department |

## LinkUrl

| field    | type                                  | description                                                  |
| -------- | ------------------------------------- | ------------------------------------------------------------ |
| name     | [CharField]({{docs_url}}#charfield)   | name of the url (displayed in kiosk mode)                    |
| url      | [URLField]({{docs_url}}#urlfield)     | url to which will be redirected                              |
| priority | [FloatField]({{docs_url}}#floatfield) | priority of the url (used for ordening)                      |
| code     | [QRCode](#qrcode)                     | The QRCode this url is linked to, reverse accessor is `urls` |

- This model is ordered by default by `-priority`

## ApiCall

| field    | type                                | description                               |
| -------- | ----------------------------------- | ----------------------------------------- |
| url      | [URLField]({{docs_url}}#urlfield)   | name of the url (displayed in kiosk mode) |
| link_url | [LinkUrl](#linkurl)                 | the LinkUrl this apicall is attached to   |
| payload  | [TextField]({{docs_url}}#textfield) | payload sent during api call              |

## Header

| field    | type                                | description                                                        |
| -------- | ----------------------------------- | ------------------------------------------------------------------ |
| api_call | [URLField]({{docs_url}}#urlfield)   | The api-call this header belongs to. Reverse accessor is `headers` |
| key      | [CharField]({{docs_url}}#charfield) | The header name (e.g. `Content-Type`)                              |
| value    | [CharField]({{docs_url}}#charfield) | The header value (e.g. `application/json`)                         |
