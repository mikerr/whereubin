# whereubin
Track location on raspberry pi, picoW or esp32 using only WIFi 

Requirements
============

raspberry pi, picoW or ESP32

Uses Google's Gelocation API
You'll need to get an API key from
https://developers.google.com/maps/documentation/geolocation/overview


Operation
=========

Scans local wifi APs every 30 seconds and logs SSID mac addresses

Later when in home WIFI range connects and gets coordinates of each point

Then sends an email with a Google Maps link of the route taken


![image](/gmap.png)
