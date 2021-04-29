#include <LiquidCrystal.h>

/* LCD pins */
#define PIN_RW 8
#define PIN_EN 9
#define PIN_D4 4
#define PIN_D5 5
#define PIN_D6 6
#define PIN_D7 7

/* Time until backlight is turned off if no update is received */
#define SCREEN_OFF_DELAY  10000

LiquidCrystal lcd(PIN_RW, PIN_EN, PIN_D4, PIN_D5, PIN_D6, PIN_D7);


char array[200];
String values[4];
String input;

void setup() {
  // Setup LCD
  lcd.begin(16, 2);
  
  // Setup serial
  Serial.begin(9600);
}

void loop() {
    
while (!Serial.available());
  input = Serial.readString();
  
  input.toCharArray(array, 200);
  
  char *p = array;
  char *str;
  int index = 0;
  while ((str = strtok_r(p, ";", &p)) != NULL) // delimiter is the semicolon
  {
    values[index] = str;
    index++;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("CPU RAM USE FREE");

  lcd.setCursor(0, 1);
  lcd.print(values[0]);

  lcd.setCursor(4, 1);
  lcd.print(values[1]);

  lcd.setCursor(8, 1);
  lcd.print(values[2]);

  lcd.setCursor(12, 1);
  lcd.print(values[3]);
}
