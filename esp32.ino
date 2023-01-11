
#include "WiFi.h"
#include <WiFiClientSecure.h>

#include <ESP_Mail_Client.h>
// https://github.com/mobizt/ESP-Mail-Client

const char *homessid = "";
const char *password = "";
String APIKEY = "";

#define GMAIL_USERNAME "@gmail.com" 
#define GMAIL_PASSWORD ""

String geolocate(String jsonlist) {

  WiFiClientSecure client;
  client.setInsecure();

  const char* server = "www.googleapis.com";
  String url = "/geolocation/v1/geolocate?key=" + APIKEY;
  int conn = client.connect(server, 443);

  if (conn == 1) {
      String body = "{\"considerIp\": \"false\",  \"wifiAccessPoints\": [ " + jsonlist +  "]}";
      int body_len = body.length();

      client.println("POST " + url +" HTTP/1.1");
      client.print("Host: "); client.println(server);
      client.println("Content-Type: application/json");
      client.print("Content-Length: "); client.println(body_len);
      client.println("Connection: Close");
      client.println();
      client.println(body);
      client.println();

      while (client.available() == 0);

      String output = "";
      while (client.available()) {
         char c = client.read();
         //Serial.write(c);
         output += c;
      }
      int pos = output.indexOf("\r\n\r\n");
      String json = output.substring(pos,-1);
      pos = json.indexOf("lat");
      String lat = json.substring(pos +6, pos + 16);
      pos = json.indexOf("lng");
      String lng = json.substring(pos +6, pos + 16);
      String latlng = lat + "," + lng;
      return (latlng);
   } else {
      client.stop();
      Serial.println("Connection Failed");
      return "";
   }
}

void sendmail(String subject, String content) {
  SMTPSession smtp;
  ESP_Mail_Session session;
  session.server.host_name = "smtp.gmail.com" ;
  session.server.port = 587;
  session.login.email = GMAIL_USERNAME;
  session.login.password = GMAIL_PASSWORD;
  session.login.user_domain = "";

  /* Declare the message class */
  SMTP_Message message;

  message.sender.name = "";
  message.sender.email = GMAIL_USERNAME;
  message.subject = subject;
  message.addRecipient("",GMAIL_USERNAME);

  //Send simple text message
  String textMsg = content;
  message.text.content = textMsg.c_str();
  message.text.charSet = "us-ascii";
  message.text.transfer_encoding = Content_Transfer_Encoding::enc_7bit; 

  if (!smtp.connect(&session));
  if (!MailClient.sendMail(&smtp, &message))
    Serial.println("Error sending Email, " + smtp.errorReason());
}

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    WiFi.begin(homessid, password);
}

int wifis = 0;
void loop()
{
  String jsonlist,ssid;

  // do a scan and log groups of wifi APs 
  int n = WiFi.scanNetworks();
  if (n > 2)  {
    // need 3 to geolocate
    for (int i = 0; i < n; ++i) {
      String macaddr = WiFi.BSSIDstr(i);
      int signal = WiFi.RSSI(i);
      ssid = WiFi.SSID(i);
      jsonlist += "{\"macAddress\": \"" + macaddr + "\", \"signalStrength\": " + signal + "},"; 
      }
    jsonlist = jsonlist.substring(0,jsonlist.length() - 1); // remove trailing comma
 
    wifis++;
  }
  // when on home wifi, upload the journey
  // process wifi groups into lat/long with google api
  if (wifis >1) {
    String latlong = geolocate(jsonlist);
    String gmap = "https://google.com/maps/dir/" + latlong; 
    Serial.println(gmap);

    sendmail("Tracking map",gmap);
  }
  delay(30000);
}
