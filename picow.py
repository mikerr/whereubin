# Stores your current location by scanning local WIFI APs
# later uses google's geolocation API to convert them to lat-long
# when in home wifi 

import network, urequests
import binascii,json,time
import umail
import os

# https://github.com/shawwwn/uMail

# Home wifi credentials
homessid = ''
password = ''
 
GMAIL_USERNAME = '@gmail.com' 
GMAIL_PASSWORD = ''  

# Google location API : https://developers.google.com/maps/documentation/geolocation/overview
APIKEY  = ""
LOGFILE = "wifilist.txt"

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

wifis = 0
if LOGFILE in os.listdir():
        wifis = 2
    
oldw1 = ""
print ("scanning")
while (wifis < 100):
    networks = wlan.scan()
    networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
    w1 = networks[0][1]
    if (w1 != oldw1): # only log when strongest wifi changes i.e. we moved away
        print (".", end='')
        wifis += 1
        jsonmacs = wifi2macs(networks)
        file = open(LOGFILE, "a")
        file.write(jsonmacs +"\n")
        file.close()
    oldw1 = w1
    
    ssid = networks[0][0].decode()
    if (ssid == homessid and wifis > 2): break
    time.sleep(30)
    
# connect to our network
print ("connecting to home wifi")
wlan = network.WLAN(network.STA_IF)
wlan.connect(homessid, password)
while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(5)

# geolocate each group of wifi ssids into lat/long
# then use them as points on a google maps route

print ("geolocating wifi points")
gmap = "https://google.com/maps/dir/"

f = open(LOGFILE)
while (line := f.readline().rstrip()):       
    payload = '{"considerIp": "false",  "wifiAccessPoints": [ ' + line +  ']}'
    headers = {'Content-Type':'application/json'}
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={APIKEY}"
    response = urequests.post(url,data=payload,headers=headers)
    
    locdata = json.loads(response.content.decode())
    print (locdata)
    if (not "error" in locdata):
      gmap += str(locdata['location']['lat']) + ',' + str(locdata['location']['lng']) + '/'
f.close()

print (gmap)
print("sending email map route")
smtp = umail.SMTP('smtp.gmail.com', 587, username=GMAIL_USERNAME, password=GMAIL_PASSWORD)
smtp.to(GMAIL_USERNAME)
smtp.send("Subject: tracking map \n\n" + gmap)
smtp.quit()

os.remove (LOGFILE)
print ("done")
