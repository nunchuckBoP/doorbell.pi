from gpiozero import Button
from signal import pause

def button_pressed():
    print("PRESSED!")
# end

def button_released():
   print("RELEASED!")
# end

button = Button(23)
button.when_pressed = button_pressed
button.when_released = button_released
pause()
