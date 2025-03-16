#include <LiquidCrystal.h>
#include <DHT.h>
#define Type DHT11
LiquidCrystal lcd(7,8,9,10,11,12);
int sensorpin = 2;
DHT HT(sensorpin, Type);
float humidity;
float temperature;
int digitalVal = 0;
bool disabled = false;
String cmd;

int ledpin = 13;
int pushbuttonpin = 4;
int buzzerpin = 5;


void setup() {
  pinMode(ledpin, OUTPUT);
  pinMode(pushbuttonpin, INPUT);
  digitalWrite(pushbuttonpin, HIGH);
  pinMode(buzzerpin, OUTPUT);
  lcd.begin(16,2);
  Serial.begin(9600);
  HT.begin();
  // put your setup code here, to run once:
}

void loop() {
  humidity = HT.readHumidity();
  temperature = HT.readTemperature();
  digitalWrite(ledpin, LOW);
  digitalWrite(buzzerpin, LOW);
  cmd = Serial.readStringUntil('\r');
  
  Serial.print(temperature);
  Serial.print(",");
  Serial.println(humidity);

  //digitalVal = digitalRead(pushbuttonpin);
  //Serial.println(digitalVal);

  digitalWrite(ledpin, LOW);
  digitalWrite(buzzerpin, LOW);

  disabled = false;

  if(cmd == "al"){
     lcd.clear();
     while(disabled == false){
         digitalVal = digitalRead(pushbuttonpin);
         
         if(digitalVal == 0){
              disabled = true;
         }

         showdetails("wake up!", 0);
         alertsequence(2);
         lcd.clear();
     }
     lcd.clear();
  }

  else if(cmd == "Hh"){
     lcd.clear();
     showdetails("humid high", 0);
     showdetails("trigger on", 1);
     triggersequence();
     lcd.clear();
  }

  else if(cmd == "Hl"){
     lcd.clear();
     showdetails("humid low", 0);
     showdetails("trigger off", 1);
     triggersequence();
     lcd.clear();
  }

  else if(cmd == "Th"){
     lcd.clear();
     showdetails("temp high", 0);
     showdetails("trigger on", 1);
     triggersequence();
     lcd.clear();
  }

  else if(cmd == "Tl"){
     lcd.clear();
     showdetails("temp low", 0);
     showdetails("trigger off", 1);
     triggersequence();
     lcd.clear();
  }
  else if(cmd.length() > 5){
     lcd.clear();
     while(disabled == false){
         digitalVal = digitalRead(pushbuttonpin);
         
         if(digitalVal == 0){
              disabled = true;
         }

         showdetails(cmd, 0);
         alertsequence(3);
         lcd.clear();
     }
     lcd.clear();
  }
  else{
    lcd.setCursor(0,0);
    lcd.print(cmd);
    lcd.setCursor(0, 1);
    lcd.print(temperature);
    lcd.print("oC");
    lcd.print(" ");
    lcd.print(humidity);
    lcd.print("%");
  }
  // put your main code here, to run repeatedly:
}

void alertsequence(int repeats){
  int i = 0;
  
  while(i < repeats){
    digitalWrite(ledpin, HIGH);
    analogWrite(buzzerpin, 50);
    delay(100);
    digitalWrite(ledpin, LOW);
    analogWrite(buzzerpin, 0);
    delay(100);
    i = i + 1;
  }

  delay(500);
}

void triggersequence(){
  digitalWrite(ledpin, HIGH);
  delay(2000);
  digitalWrite(ledpin, LOW);
}

void showdetails(String detail, int row){
  lcd.setCursor(0, row);
  lcd.print(detail);
}
