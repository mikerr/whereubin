# Stores your current location by scanning local WIFI APs
# later uses google's geolocation API to convert them to lat-long
# when in home wifi 

import network, urequests
import binascii, json

ssid = 'yourSSID'
password = ''

# Google location API : https://developers.google.com/maps/documentation/geolocation/overview
APIKEY  = "" #YOUR_API_KEY

# scan our networks

wlan = network.WLAN()
wlan.active(True)
networks = wlan.scan() 

wifidata = ""
for w in networks:
      hex = binascii.hexlify(w[1]).decode()
      macaddr = ':'.join(hex[i]+hex[i+1] for i in range(0, len(hex), 2))
      signal = w[3]
      macjson =  f'"macAddress": "{macaddr}", "signalStrength": {signal}'
      wifidata += '{' + macjson + '},'

wifidata = wifidata[:-1] # strip off trailing comma
    
# connect to our network
wlan = network.WLAN(network.STA_IF)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        
payload = '{"considerIp": "false",  "wifiAccessPoints": [ ' + wifidata +  ']}'
headers = {'Content-Type':'application/json'}
url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={APIKEY}"
response = urequests.post(url,data=payload,headers = headers)

locdata = json.loads(response.content.decode())
lat = (locdata['location']['lat'])
lng = (locdata['location']['lng'])

print (f"https://maps.google.com/?q={lat},{lng}")
print (f"https://google.com/maps/{lat},{lng}")
