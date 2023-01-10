# whereubin
Track location on picoW or esp32 using only WIFi 

Uses Google's Gelocation API
You'll need to get an API key from
https://developers.google.com/maps/documentation/geolocation/overview


Operation
=========

Scans local wifi APs every 30 seconds and logs SSID mac addresses
Later when in home WIFI range connects and gets coordinates of each point
Sends an email with a Google Maps link of the route taken

![image](/gmap.png)
