# Qr Toolkit Core

The Qr Toolkit core is a django app, capable of linking your object to a QR code. This creates the possibility to relate an object with a qr code, and updating the qr code without re-printing and re-applying it to said object.

Every QR code can have multiple links, to which will be redirected. If, later, you update these urls, the qr code will redirect to the updated link. Depending on the mode of the qr code (Redirect, Kiosk, Basic Info, Api call), the behaviour will be slightly different. This is explained [here](./modes.md)

The example repository, which holds all changes made in these tutorials, can be [found here](https://github.com/lab9k/qr-toolkit-core-example)
