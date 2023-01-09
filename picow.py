# Stores your current location by scanning local WIFI APs
# later uses google's geolocation API to convert them to lat-long
# when in home wifi 

import network, urequests
import binascii,json, time
import umail 
# https://github.com/shawwwn/uMail

# Home wifi credentials
ssid = ''
password = ''
 
GMAIL_USERNAME = '' 
GMAIL_PASSWORD = ''  

# Google location API : https://developers.google.com/maps/documentation/geolocation/overview
APIKEY  = "" #YOUR_API_KEY
    
def wifi2macs (networks) :
    # convert networks to json list of mac addresses and signal strengths
    wifidata = ""
    for w in networks[:3]: # only top 3 signal strengths
          hex = binascii.hexlify(w[1]).decode()
          macaddr = ':'.join(hex[i]+hex[i+1] for i in range(0, len(hex), 2))
          signal = w[3]
          macjson =  f'"macAddress": "{macaddr}", "signalStrength": {signal}'
          wifidata += '{' + macjson + '},'

    wifidata = wifidata[:-1] # strip off trailing comma   
    return (wifidata)

# scan our networks

wlan = network.WLAN()
wlan.active(True)

wifis = []
oldw1 = ""

print ("scanning")
while (len(wifis) < 2):
    networks = wlan.scan()
    networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
    w1 = networks[0][0]
    if (w1 != oldw1): # only log when strongest wifi changes i.e. we moved away
        wifis.append (wifi2macs(networks))
    oldw1 = w1
    
# connect to our network
wlan = network.WLAN(network.STA_IF)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(5)

# geolocate each group of wifi ssids into lat/long
# then use them as points on a google maps route

gmap = "https://google.com/maps/dir/"
for wifidata in wifis:
    payload = '{"considerIp": "false",  "wifiAccessPoints": [ ' + wifidata +  ']}'
    headers = {'Content-Type':'application/json'}
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={APIKEY}"
    response = urequests.post(url,data=payload,headers=headers)
    
    locdata = json.loads(response.content.decode())
    print (locdata)
    gmap += str(locdata['location']['lat']) + ',' + str(locdata['location']['lng']) + '/'

smtp = umail.SMTP('smtp.gmail.com', 587, username=GMAIL_USERNAME, password=GMAIL_PASSWORD)
smtp.to(GMAIL_USERNAME)
smtp.send("\n" + gmap)
smtp.quit()

print (gmap)    
