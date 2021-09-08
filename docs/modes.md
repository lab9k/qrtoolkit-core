# Modes

There are currently 4 modes implemented in the qr toolkit, all of them display a slightly different behaviour.

## Basic Information mode

This is the simplest of modes for the qr codes. This mode will solely be used to display the `basic_info`, configured in the qr code instance. The template for this mode can be overridden following the [theming tutorial](./theming.md)

## Redirect mode

A QR code in Redirect mode will redirect the user to the url, linked to itself, with the highest priority. This allows for multiple urls to be configured, and altering priority will redirect to different sites.

## Kiosk Mode

A qr code in Kiosk mode will, when scanned, display all url it has configured, allowing the user to choose his own destination url. This template can also be overridden according to the [theming tutorial](./theming.md)

## Api Call mode

This mode is exactly the same as Kiosk mode, but when a button is pressed, an extra call to the qr toolkit is made, which will then execute all configured api calls related to that specific button. After completion, the user is redirected to the specified url.
