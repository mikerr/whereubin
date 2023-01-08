
#include "WiFi.h"
#include <WiFiClientSecure.h>

const char *ssid = "SSID";
const char *password = "password";
String APIKEY = "YOUR_API_KEY";

const char* server = "www.googleapis.com";
String url = "/geolocation/v1/geolocate?key=" + APIKEY;

WiFiClientSecure client;

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    
    WiFi.begin(ssid, password);

    client.setInsecure();
}

void loop()
{
  String jsonlist;

  int n = WiFi.scanNetworks();
  if (n > 2) // need 3 to geolocate
   for (int i = 0; i < n; ++i) {
    String macaddr = WiFi.BSSIDstr(i);
    int signal = WiFi.RSSI(i);
    
    jsonlist += "{\"macAddress\": \"" + macaddr + "\", \"signalStrength\": " + signal + "},"; 
  }
  jsonlist = jsonlist.substring(0,jsonlist.length() - 1); // remove trailing comma

  String georequest = "{\"considerIp\": \"false\",  \"wifiAccessPoints\": [ " + jsonlist +  "]}";

  int  conn;
   
   String body = georequest;
   int body_len = body.length();

   conn = client.connect(server, 443);

   if (conn == 1) {
      Serial.println(); Serial.print("Sending Parameters...");
      //Request
      client.println("POST " + url +" HTTP/1.1");
      //Headers
      client.print("Host: "); client.println(server);
      client.println("Content-Type: application/json");
      client.print("Content-Length: "); client.println(body_len);
      client.println("Connection: Close");
      client.println();
      //Body
      client.println(body);
      client.println();

      //Wait for server response
      while (client.available() == 0);

      //Print Server Response
      while (client.available()) {
         char c = client.read();
         Serial.write(c);
      }
   } else {
      client.stop();
      Serial.println("Connection Failed");
   }

  delay(10000);
}
