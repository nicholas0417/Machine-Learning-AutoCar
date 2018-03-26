#include <SoftwareSerial.h> 
#include <LiquidCrystal_I2C.h>  
#define MAX_BTCMDLEN 128

// assign pin num
int right_pin = 6;
int left_pin = 7;
int forward_pin = 10;
int reverse_pin = 9;
int time =500;

// 7seg display
int resistor_pin = 1;  //  for control speed    analog pin 1
int sensorValue = 0;       
int setSpeed;
int preValue = 0;
int outputs[4] = {2,3,4,5}; 
byte BCD[10][4] ={{0,0,0,0},   // 0
                  {1,0,0,0},   // 1
                  {0,1,0,0},   // 2
                  {1,1,0,0},   // 3
                  {0,0,1,0},   // 4
                  {1,0,1,0},   // 5
                  {0,1,1,0},   // 6
                  {1,1,1,0},   // 7
                  {0,0,0,1},   // 8
                  {1,0,0,1},   // 9
                   }; //BCD code

// bluetooth & LCD
SoftwareSerial BTSerial(12, 13);   // 定義連接藍牙模組的序列埠 , 傳送腳 TX / 接收腳 RX
LiquidCrystal_I2C lcd(0x27,16,2);  

void setup() {
  Serial.begin(9600);              
  BTSerial.begin(9600);           
  
  for(int dig = 0; dig < 4; dig++){
      pinMode(outputs[dig], OUTPUT);
  }
  Serial.println("BT is ready!");
  pinMode(right_pin, OUTPUT);
  pinMode(left_pin, OUTPUT);
  pinMode(forward_pin, OUTPUT);
  pinMode(reverse_pin, OUTPUT);
  // ----------------------------------------------
  lcd.init();            // initialize the lcd
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("BT is Ready  ");
  lcd.print(time);
  lcd.setCursor(0,1);
  lcd.print("Check the device");
  // -----------------------------------------------
}

void loop() {
  int size = 0;                   
  int len = 0;                    
  byte data[MAX_BTCMDLEN]="" ;        
  char word[MAX_BTCMDLEN]="" ;        
  //----------------------------------------------------------------------------
  sensorValue = analogRead(resistor_pin);
  setSpeed = round(sensorValue)/128*1.2;
  if((setSpeed != preValue) ){
    preValue = setSpeed;
    Serial.println(setSpeed, DEC);
    time = setSpeed*100;
    for(int dig = 0; dig < 4; ++dig){
       digitalWrite(outputs[dig], BCD[setSpeed][dig]);
    }
    delay(500);
  }
  //---------------------------------------------------------------------------------
  while( size < MAX_BTCMDLEN ){                               // [有待修改]                
     if (BTSerial.available()) {
           data[(len++)%MAX_BTCMDLEN]=char(BTSerial.read());  
     }else{
          size++;                                              
     }
  }
  //-------------------------------------------------------------------------
  if( len ){ 
      sprintf(word,"%s",data);                               
      Serial.print(word);
      send_command(atoi(word),time);
  }else{
      reset();
  }
  //-----------------------------------------------------------------------------
}

// --------------------------------------------------------------------------------------------
void right(int time){
  digitalWrite(right_pin, HIGH);
  lcd.setCursor(0,0);
  lcd.print("Command:        ");
  lcd.setCursor(0,1);
  lcd.print("only right      ");
  delay(time);
}

void left(int time){
  
  digitalWrite(left_pin, HIGH);
  lcd.setCursor(0,0);
  lcd.print("Command:         ");
  lcd.setCursor(0,1);
  lcd.print("only left        ");
  delay(time);
  
}

void forward(int time){
  
  digitalWrite(forward_pin, HIGH);
  lcd.setCursor(0,0);
  lcd.print("Command:         ");
  lcd.setCursor(0,1);
  lcd.print("only forward     ");
  delay(time);
}

void reverse(int time){
  digitalWrite(reverse_pin, HIGH);
  lcd.setCursor(0,0);
  lcd.print("Command:        ");
  lcd.setCursor(0,1);
  lcd.print("only reverse    ");
  delay(time);
}

void forward_right(int time){
  digitalWrite(right_pin, HIGH);
  delay(time);
  digitalWrite(forward_pin, HIGH);
  delay(time);
  
  lcd.setCursor(0,0);
  lcd.print("Command:        ");
  lcd.setCursor(0,1);
  lcd.print("forward right     ");
}

void reverse_right(int time){
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(right_pin, HIGH);
  lcd.setCursor(0,0);
  lcd.print("Command:         ");
  lcd.setCursor(0,1);
  lcd.print("reverse right    ");
}

void forward_left(int time){
  digitalWrite(left_pin, HIGH);
  delay(time);
  digitalWrite(forward_pin, HIGH);
  delay(time);
  
  lcd.setCursor(0,0);
  lcd.print("Command:       ");
  lcd.setCursor(0,1);
  lcd.print("forward left    ");
}

void reverse_left(int time){
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(left_pin, HIGH);
  
  lcd.setCursor(0,0);
  lcd.print("Command:          ");
  lcd.setCursor(0,1);
  lcd.print("reverse left      ");
  delay(time);
}
// --------------------------------------------------------------------------------------------
void reset(){
  digitalWrite(right_pin, LOW);
  digitalWrite(left_pin, LOW);
  digitalWrite(forward_pin, LOW);
  digitalWrite(reverse_pin, LOW);
}

void send_command(int command, int time){
  switch (command){

     //reset command
     case 0: reset(); break;

     // single command
     case 1: forward(time); Serial.println(" forward"); break;
     case 2: reverse(time); Serial.println(" reverse"); break;
     case 3: right(time);   Serial.println(" right");   break;
     case 4: left(time);    Serial.println(" left");    break;

     //combination command
     case 6: forward_right(time); Serial.println(" forward_right"); break;
     case 7: forward_left(time);  Serial.println(" forward_left"); break;
     case 8: reverse_right(time); Serial.println(" reverse_right"); break;
     case 9: reverse_left(time);  Serial.println(" reverse_left"); break;

     default: reset(); Serial.print(" Inalid Command\n");
    }
}
