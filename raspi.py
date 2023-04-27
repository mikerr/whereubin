# Stores your current location by scanning local WIFI APs
# later uses google's geolocation API to convert them to lat-long
# when in home wifi 

import wifi,requests
import json,time
import smtplib
import os

# Home wifi credentials
homessid = ''
password = ''
 
GMAIL_USERNAME = '@gmail.com' 
GMAIL_PASSWORD = ''  # app password

# Google location API : https://developers.google.com/maps/documentation/geolocation/overview
APIKEY  = ""
LOGFILE = "wifilist.txt"

def wifi2macs (networks) :
    # convert to json list of mac addresses and signal strengths
    wifidata = ""
    for wlan in networks:
        #print(wlan.ssid, wlan.address, wlan.signal)
        macjson =  f'"macAddress": "{wlan.address}", "signalStrength": {wlan.signal}'
        wifidata += '{' + macjson + '},'

    wifidata = wifidata[:-1] # strip off trailing comma   
    return (wifidata)

# scan our networks

wifis = 0
if LOGFILE in os.listdir():
        wifis = 2
    
oldw1 = ""
print ("scanning")
while (wifis < 100):
    networks = wifi.Cell.all('wlan0')
    w1 = ""
    for wlan in networks:
        w1 = wlan.ssid
        break
    print (wifis)
    if (w1 != oldw1): # only log when strongest wifi changes i.e. we moved away
        print (".", end='')
        wifis += 1
        jsonmacs = wifi2macs(networks)
        file = open(LOGFILE, "a")
        file.write(jsonmacs +"\n")
        file.close()
    oldw1 = w1
    
    if (w1 == homessid and wifis > 2): break
    time.sleep(30)
    
# connect to our network
print ("connected to home wifi")

# geolocate each group of wifi ssids into lat/long
# then use them as points on a google maps route

print ("geolocating wifi points")
gmap = "https://google.com/maps/dir/"

f = open(LOGFILE)
while (line := f.readline().rstrip()):       
    payload = '{"considerIp": "false",  "wifiAccessPoints": [ ' + line +  ']}'
    headers = {'Content-Type':'application/json'}
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={APIKEY}"
    response = requests.post(url,data=payload,headers=headers)
    
    locdata = json.loads(response.content.decode())
    print (locdata)
    if (not "error" in locdata):
      gmap += str(locdata['location']['lat']) + ',' + str(locdata['location']['lng']) + '/'
f.close()

print (gmap)
print("sending email map route")
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
server.sendmail(GMAIL_USERNAME,GMAIL_USERNAME,"Subject: tracking map \n\n" + gmap)
server.close()

os.remove (LOGFILE)
print ("done")
