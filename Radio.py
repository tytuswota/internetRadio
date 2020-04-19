import smbus
import time
import datetime
import os
import RPi.GPIO as GPIO

I2C_ADDR = 0x27
LCD_WIDTH = 16

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

LCD_BACKLIGHT = 0x08

ENABLE = 0b00000100

E_PULSE = 0.0005
E_DELAY = 0.0005

bus = smbus.SMBus(1) 

#buttons for controlling the channels and volume
NEXT_C = 4
PREV_C = 17
PAUSE = 27
VOL_UP = 26
VOL_DOWN = 19

def lcd_init():
  lcd_byte(0x33,LCD_CMD) 
  lcd_byte(0x32,LCD_CMD) 
  lcd_byte(0x06,LCD_CMD) 
  lcd_byte(0x0C,LCD_CMD) 
  lcd_byte(0x28,LCD_CMD) 
  lcd_byte(0x01,LCD_CMD) 
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def main():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(NEXT_C, GPIO.IN)
  GPIO.setup(PREV_C, GPIO.IN)
  GPIO.setup(PAUSE, GPIO.IN)
  GPIO.setup(VOL_UP, GPIO.IN)
  GPIO.setup(VOL_DOWN, GPIO.IN)
  volume = 80
  
  lcd_init()
  
  play_pause_button = False

  while True:
    if(GPIO.input(NEXT_C) == 1):
        os.system("mpc next")
        time.sleep(1)
        os.system("mpc play")
    if(GPIO.input(PREV_C) == 1): 
        os.system("mpc prev")
        time.sleep(1)
        os.system("mpc play")
    if(GPIO.input(PAUSE) == 1):
        play_pause_button = not play_pause_button
        if(play_pause_button):
            os.system("mpc play")
        else:
            os.system("mpc pause")
        time.sleep(1)
    if(GPIO.input(VOL_UP) == 1):
        if(volume != 100):
            volume += 10
            os.system("mpc volume " + str(volume))
    if(GPIO.input(VOL_DOWN) == 1):
        if(volume != 0):
            volume -= 10
            os.system("mpc volume " + str(volume))
    if(GPIO.input(VOL_DOWN) == 1 or GPIO.input(VOL_UP) == 1):
        
        f=os.popen("mpc volume")
    
        vol = ""
    
        for i in f.readlines():
            vol += i
        
        lcd_string(vol,LCD_LINE_2)
        time.sleep(0.5)
        lcd_string("",LCD_LINE_2)
    
    f=os.popen("mpc current")
    
    station = ""
    
    for i in f.readlines():
        station += i
        
    lcd_string(station,LCD_LINE_1)
    time.sleep(1)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)

