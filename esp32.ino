
#include "WiFi.h"
#include <WiFiClientSecure.h>

#include <ESP_Mail_Client.h>
// https://github.com/mobizt/ESP-Mail-Client

const char *ssid = "";
const char *password = "";
String APIKEY = "";

#define GMAIL_USERNAME "@gmail.com" 
#define GMAIL_PASSWORD ""

WiFiClientSecure client;
SMTPSession smtp;

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

  // do a scan and log wifi APs
  int n = WiFi.scanNetworks();
  if (n > 2) // need 3 to geolocate
   for (int i = 0; i < n; ++i) {
    String macaddr = WiFi.BSSIDstr(i);
    int signal = WiFi.RSSI(i);
    Serial.println(WiFi.SSID(i));
    jsonlist += "{\"macAddress\": \"" + macaddr + "\", \"signalStrength\": " + signal + "},"; 
  }
  jsonlist = jsonlist.substring(0,jsonlist.length() - 1); // remove trailing comma

  const char* server = "www.googleapis.com";
  String url = "/geolocation/v1/geolocate?key=" + APIKEY;
  int conn = client.connect(server, 443);

  if (conn == 1) {
      String body = "{\"considerIp\": \"false\",  \"wifiAccessPoints\": [ " + jsonlist +  "]}";
      int body_len = body.length();

      Serial.println(); Serial.print("Sending Georequest");
      client.println("POST " + url +" HTTP/1.1");
      client.print("Host: "); client.println(server);
      client.println("Content-Type: application/json");
      client.print("Content-Length: "); client.println(body_len);
      client.println("Connection: Close");
      client.println();
      client.println(body);
      client.println();

      while (client.available() == 0);

      while (client.available()) {
         char c = client.read();
         Serial.write(c);
      }
   } else {
      client.stop();
      Serial.println("Connection Failed");
   }
  String gmap = "https://google.com/maps/dir/"; 
  Serial.println(gmap);

  ESP_Mail_Session session;
  session.server.host_name = "smtp.gmail.com" ;
  session.server.port = 587;
  session.login.email = GMAIL_USERNAME;
  session.login.password = GMAIL_PASSWORD;
  session.login.user_domain = "";

  /* Declare the message class */
  SMTP_Message message;

  message.sender.name = "ESP32";
  message.sender.email = GMAIL_USERNAME;
  message.subject = "Tracking map";
  message.addRecipient("Microcontrollerslab",GMAIL_USERNAME);

  //Send simple text message
  String textMsg = gmap;
  message.text.content = textMsg.c_str();
  message.text.charSet = "us-ascii";
  message.text.transfer_encoding = Content_Transfer_Encoding::enc_7bit; 

  if (!smtp.connect(&session));
  if (!MailClient.sendMail(&smtp, &message))
    Serial.println("Error sending Email, " + smtp.errorReason());

  delay(30000);
}
