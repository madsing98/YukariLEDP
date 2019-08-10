# Import libraries
import time           # Time management functions
import tkinter as tk  # Tkinter GUI
import sys            # Library to check platform/OS
import os             # Used to change current directory
import random         # Random number generator library
from subprocess import call

# System variable, when InSitu == False the app does not access any GPIO, SPI, ...
if(sys.platform == 'linux'):
    InSitu = True    # Running on the Yukari Raspberry Pi
else:
    InSitu = False   # Running on the Mac for development.

# Change current directory so that all file resources can be opened simply
if InSitu:
    os.chdir('/home/pi/Documents/LEDController')

# Initialize the random number generator
random.seed()

# GUI Definitions
MainFont = 'Roboto Light'
if(InSitu):
    LargeFontSize = '18'
    SmallFontSize = '14'
else:
    LargeFontSize = '24'
    SmallFontSize = '18'
MainBackColor = '#505050'
MainFrontColor = 'white'
MainToolbarColor = '#808080'
EditBackColor = 'light grey'
EditFrontColor = 'dark slate grey'
ButtonBackColor = 'grey'
ButtonFrontColor = 'orange'
ListFrameListboxHeight = 12
ButtonPadY = 10
ButtonPadX = 10
LabelPadX = 15
LabelPadY = 10
FieldPadX = 15
FieldPadY = 5
FieldBorderWidth = 2

# Hardware support
if InSitu:
    # Initialize the INA219 DC Current Sensor on the i2C interface
    # Use SDA and SCL pins to communicate with the INA219 module
    # Uses the pi-ina219 library
    from ina219 import INA219
    from ina219 import DeviceRangeError
    SHUNT_OHMS = 0.1
    ina = INA219(SHUNT_OHMS)    # shunt_ohms: The value of the shunt resistor in Ohms
                                # address: The I2C address of the INA219 (optional), defaults to 0x40
    try:
        ina.configure()
    except:
        ina219Present = False
    else:
        ina219Present = True

    # Initialize the SPI interface
    # Use MOSI and SCLK pins to communicate with the LED modules
    import spidev   # SPI bus development library
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.mode = 0
    spi.bits_per_word = 8       # 8 bits per word, looks like it's the only value working
    spi.max_speed_hz = 8000000  # 8 MHz

    # Initialize the com port to communicate with the SkyLED Arduino
    import serial         # Serial communication library
    SkyLEDSerial = serial.Serial("/dev/ttyUSB0", 115200)    # Serial communication through the USB port at 115200 bits per second
                                                            # Side effect: this command also resets/reboots the SkyLED Arduino

SkyLEDColor = [0, 0, 0, 0, 0, 0, 0, 0]


# tkinter windows hierarchy
# win
# |- MainFrame
# |- ListFrame
# |- TestFrame
# Create the main window and maximize it
win = tk.Tk()
win.title("YukariLED")  # This title will not appear
if InSitu:
    win.attributes('-fullscreen', True)
    win.config(cursor='none')

# Create three frames, MainFrame, ListFrame and TestFrame, all covering the entire screen / window,
# that will be raised when required to display their own widgets
# The mainframe is the main control screen
MainFrame = tk.Frame(win, bg=MainBackColor, height=480, width=800)
MainFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S+tk.W)
MainFrame.grid_propagate(False)

# The ListFrame is called after the Edit button is pressed and displays a list of all the lights
ListFrame = tk.Frame(win, bg=MainBackColor, height=480, width=800)
ListFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S+tk.W)
ListFrame.grid_propagate(False)

# The TestFrame is called when a light is being tested
# TestFrameCurrentValue  is used to store the current value of the LED brightness
# TestFrameCurrentLight  is used to store the light being tested
TestFrame = tk.Frame(win, bg=MainBackColor, height=480, width=800)
TestFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S+tk.W)
TestFrame.grid_propagate(False)
TestFrameActive = False   # Used to stop the automatic update of the lights when we are in test mode

# Global variables for automatic Day/Night mode and Sky light on/off
auto_day_night = False
sky_on = True

# Initialize the LEDCommand message to be sent through the SPI interface
# LEDCommandSingle and LEDAllOffSingle are single messages for a single LED PWM module
# LEDCommand and LEDAllOff are complete messages for "number_of_LED_modules" modules
# !!!!! The first message goes to the LAST LED module on the chain (= farthest from the Raspberry Pi)
# !!!!! The last message goes to the FIRST LED module on the chain (= module #0 = closest to the Raspberry Pi)
# BLANK = 0  LEDs not blanked
# DSPRPT = 1 PWM cycles auto repeat
# TMGRST = 0 GS counters are not reset when a new command is received
# EXTGCK = 0 Internal clock
# OUTTMG = 1
#
#                           OE   TD
#                           UX   MSB
#                           TT   GPL
#                           TG   RRA
#                           MC   SPN
#                     25h   GK   TTKBCB       BCG        BCR     OUTB3 OUTG3 OUTR3/OUTB2 OUTG2 OUTR2/OUTB1 OUTG1 OUTR1/OUTB0 OUTG0 OUTR0
LEDCommandSingle = [0b10010110, 0b01011111, 0b11111111, 0b11111111, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
LEDAllOffSingle = [0b10010110, 0b01111111, 0b11111111, 0b11111111, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Duplicate LEDCommandSingle and LEDAllOffSingle "number_of_LED_modules" times into LEDCommand and LEDAllOff
NumberOfLEDModules = 15
LEDCommand = []
LEDAllOff = []
for _ in range(NumberOfLEDModules):
    LEDCommand.extend(LEDCommandSingle)
    LEDAllOff.extend(LEDAllOffSingle)


###############################################
# Function to set an LED brightness in the LEDCommand message
# This function DOES NOT SEND the LEDCommand message to the SPI bus
# Modules are numbered 0 to number_of_LED_modules
# Module #0 is the closest to the Raspberry Pi
# A module has 12 ports numbered 0 to 11
# LED brightness values in the command are 16-bit integers (0-65535)
# The "value" parameter is in the range 0 (off) to 1000 (brightest)
# The "value" parameter is gamma corrected before being stored in LEDCommand
def SetLEDBrightness(led, value):
    global LEDCommand
    global SkyLEDColor

    if value >= 0 and value <= 1000:
        # Gamma correction
        value = int(65535.00*(float(value)/1000.00)**(1.8))

        if led['module'] == SkyLEDModule:
            SkyLEDColor[led['port']] = value >> 4
        elif led['module'] < NumberOfLEDModules and led['port'] < 12:
            # Compute the particular LED/port control word position in LEDCommand
            # The length of the message is 28 bytes per LED module
            # Each LED/port occupies 16 bits (two bytes)
            pos = 26 - led['port']*2 + (NumberOfLEDModules-1-led['module'])*28
            # Write the LED value into LEDCommand
            LEDCommand[pos] = value >> 8     # MSB
            LEDCommand[pos+1] = value & 255  # LSB


# Initialize light_list from the file 'light_list.py'
SkyLEDModule = 100
from light_list import *

# Save light_list modules and ports to a text file for debugging / reference
previous_module = -1
with open('light_list_table.txt', 'w') as fp:
    for led in sorted(light_list, key=lambda k: k['module']*100+k['port']):
        if led['module'] != previous_module:
            previous_module = led['module']
            print("\n--- Module {:2d} --------------------------".format(led['module']), file=fp)
        print("Port {:2d}: {}".format(led['port'], led['name']), file=fp)

# Global Day/Night time variables
last_day_night_switch_time = -1000.0
day_night_auto_period = 180
going_to_night = False
going_to_day = True
# led_skyR['time_to_day'][-1]
day_night_transition_length = 60  # ????????????????????????????????????????????? Improve


# Compute the values and (random) times of the sequences for all 'Random Day/Night' LEDs
def RandomizeDayNightTime():
    for led in light_list:
        if led['mode'] == 'Random Day/Night':
            time = round(random.uniform(10.0, 30.0), 1)
            led['time_to_night'] = [0, time, time+0.2, 60]
            led['value_to_night'] = [led['value_day'], led['value_day'], led['value_night'], led['value_night']]
            time = round(random.uniform(10.0, 30.0), 1)
            led['time_to_day'] = [0, time, time+0.2, 60]
            led['value_to_day'] = [led['value_night'], led['value_night'], led['value_day'], led['value_day']]


# Initialize all the constant LEDs values
def InitConstantLEDs():
    for led in light_list:
        if led['mode'] == 'Constant':
            SetLEDBrightness(led, led['value'])


# Send and store the startup value of the sky LEDs to the SkyLED Arduino
def StoreStartupSkyLED():
    for led in light_list:
        if led['module'] == SkyLEDModule:
            SetLEDBrightness(led, led['value_to_night'][0])
    if InSitu:
        SkyLEDMsg = '<'
        for v in SkyLEDColor:
            SkyLEDMsg = SkyLEDMsg + "%0.3X" % v
        SkyLEDMsg = SkyLEDMsg + '$'
        SkyLEDSerial.write(SkyLEDMsg.encode('utf-8'))
        # Debugging message:
        # print('Sent: ' + SkyLEDMsg)


# Function to compute the brightness of an LED (led) based on the current time (c_time)
# Brightness values are interpolated from the sequence event tables
def UpdateLED(c_time, led):
    # Processing of Sky On/Off switch
    # If the current led has its 'switch' key defined and equal to 'Sky' and the Sky switch is off
    # then just set the led brightness to zero
    if (not sky_on) and 'switch' in led and (led['switch'] == 'Sky'):
        SetLEDBrightness(led, 0)
        return
    # LED Mode Cycle
    if led['mode'] == 'Cycle':
        c_time = c_time % led['time'][-1]
        for ev in range(0, len(led['time'])-1):
            if c_time <= led['time'][ev+1]:
                SetLEDBrightness(led, int(led['value'][ev]+(c_time-led['time'][ev])*(
                    led['value'][ev+1]-led['value'][ev])/(led['time'][ev+1]-led['time'][ev])))
                return
        return
    # LED Mode Day/Night and Random Day/Night
    if led['mode'] in ('Day/Night', 'Random Day/Night'):
        c_time = c_time - last_day_night_switch_time
        if going_to_night:
            if c_time >= led['time_to_night'][-1]:
                SetLEDBrightness(led, int(led['value_to_night'][-1]))
                return
            for ev in range(0, len(led['time_to_night'])-1):
                if c_time <= led['time_to_night'][ev+1]:
                    SetLEDBrightness(led, int(led['value_to_night'][ev]+(c_time-led['time_to_night'][ev])*(
                        led['value_to_night'][ev+1]-led['value_to_night'][ev])/(led['time_to_night'][ev+1]-led['time_to_night'][ev])))
                    return
        if going_to_day:
            if c_time >= led['time_to_day'][-1]:
                SetLEDBrightness(led, int(led['value_to_day'][-1]))
                return
            for ev in range(0, len(led['time_to_day'])-1):
                if c_time <= led['time_to_day'][ev+1]:
                    SetLEDBrightness(led, int(led['value_to_day'][ev]+(c_time-led['time_to_day'][ev])*(
                        led['value_to_day'][ev+1]-led['value_to_day'][ev])/(led['time_to_day'][ev+1]-led['time_to_day'][ev])))
                    return
        return


# Function to trigger change to night time
# Known bug: this function does not properly manage the dayNightUpdate callback when called directly from the button event
def go_to_night(event=0):
    global last_day_night_switch_time
    global going_to_night
    global going_to_day
    now = time.perf_counter()
    if not going_to_night:
        # We were not going to night, first touch of the button, initiate transition
        if going_to_day and (now - last_day_night_switch_time) < day_night_transition_length:
            # We were transitioning to day
            last_day_night_switch_time = 2 * now - last_day_night_switch_time - day_night_transition_length
        else:
            # We were during the day
            RandomizeDayNightTime()
            last_day_night_switch_time = now
    else:
        # We were already going to night, second touch of the button,
        # force immediate transition (actually day_night_transition_length ago)
        last_day_night_switch_time = now - float(day_night_transition_length)
    going_to_night = True
    going_to_day = False


# Function to trigger change to day time
# Known bug: this function does not properly manage the dayNightUpdate callback when called directly from the button event
def go_to_day(event=0):
    global last_day_night_switch_time
    global going_to_night
    global going_to_day
    now = time.perf_counter()
    if not going_to_day:
        # We were not going to day, first touch of the button, initiate transition
        if going_to_night and (now - last_day_night_switch_time) < day_night_transition_length:
            # We were transitioning to night
            last_day_night_switch_time = 2 * now - last_day_night_switch_time - day_night_transition_length
        else:
            # We were during the night
            RandomizeDayNightTime()
            last_day_night_switch_time = now
    else:
        # We were already going to day, second touch of the button,
        # force immediate transition (actually day_night_transition_length ago)
        last_day_night_switch_time = now - float(day_night_transition_length)
    going_to_night = False
    going_to_day = True


# Button service functions
def MainFrameExitButtonPressed(event=0):
    if InSitu:
        # Switch off all LEDs and close the SPI interface
        spi.writebytes(LEDAllOff)
        time.sleep(0.1)
        spi.close()
    # Exit
    win.destroy()


def MainFrameShutdownButtonPressed(event=0):
    if InSitu:
        # Switch off all LEDs and close the SPI interface
        spi.writebytes(LEDAllOff)
        time.sleep(0.1)
        spi.close()
        # Exit and shutdown
        call("sudo shutdown -h now", shell=True)
    win.destroy()


def MainFrameEditButtonPressed(event=0):
    ListFrame.tkraise()
    if InSitu:
        win.config(cursor='arrow')


def ListFrameBackButtonPressed(event=0):
    MainFrame.tkraise()
    if InSitu:
        win.config(cursor='none')


def ListFrameTestButtonPressed(event=0):
    global TestFrameCurrentLight
    global TestFrameCurrentValue
    global TestFrameActive

    # Get the name of the light from the Listbox
    Name = ListFrameListbox.get(tk.ACTIVE)
    # TestFrameCurrentLight will point to the Light (which is a dictionary) currently being tested
    TestFrameCurrentLight = next(item for item in light_list if item['name'] == Name)

    # Copy the values of TestFrameCurrentLight into the corresponding TestFrame widgets
    TestFrameNameField.configure(text=TestFrameCurrentLight['name'])
    TestFrameModuleField.configure(text=TestFrameCurrentLight['module'])
    TestFramePortField.configure(text=TestFrameCurrentLight['port'])

    if TestFrameCurrentLight['mode'] == 'Constant':
        TestFrameCurrentValue = TestFrameCurrentLight['value']
    else:
        TestFrameCurrentValue = 500
    TestFrameValueField.configure(text=TestFrameCurrentValue)

    # Record the fact that we are in the TestFrame
    # Used to stop the automatic update of the lights when we are in test mode
    TestFrameActive = True
    TestFrame.tkraise()


def TestFrameBackButtonPressed(event=0):
    global TestFrameActive
    TestFrameActive = False
    ListFrame.tkraise()


def MainFrameAutoButtonPressed(event=0):
    global auto_day_night
    if not auto_day_night:
        MainFrameAutoButton["image"] = onButtonImage
        auto_day_night = True
    else:
        MainFrameAutoButton["image"] = offButtonImage
        auto_day_night = False
    dayNightUpdate()


def MainFrameSkyButtonPressed(event=0):
    global sky_on
    if not sky_on:
        MainFrameSkyButton["image"] = onButtonImage
        sky_on = True
    else:
        MainFrameSkyButton["image"] = offButtonImage
        sky_on = False


# Load tkinter images
exitButtonImage = tk.PhotoImage(file="icons8-close_window.gif")
shutdownButtonImage = tk.PhotoImage(file="icons8-shutdown.gif")
editButtonImage = tk.PhotoImage(file="icons8-edit-row.gif")
nightButtonImage = tk.PhotoImage(file="icons8-moon_symbol.gif")
nightOnButtonImage = tk.PhotoImage(file="icons8-moon_symbol_shine.gif")
dayButtonImage = tk.PhotoImage(file="icons8-sun.gif")
dayOnButtonImage = tk.PhotoImage(file="icons8-sun_shine.gif")
onButtonImage = tk.PhotoImage(file="icons8-toggle_on.gif")
offButtonImage = tk.PhotoImage(file="icons8-toggle_off.gif")

# Create tkinter mainframe widgets
# Create mainframe toolbar frame and toolbar widgets
MainFrameToolbar = tk.Frame(MainFrame, bg=MainToolbarColor)
MainFrameToolbar.grid(column=0, columnspan=4, row=0, sticky=tk.W + tk.E)

MainFrameShutdownButton = tk.Label(MainFrameToolbar, image=shutdownButtonImage, bg=MainToolbarColor)
MainFrameShutdownButton.grid(column=0, row=0, padx=ButtonPadX, pady=ButtonPadY)

MainFrameExitButton = tk.Label(MainFrameToolbar, image=exitButtonImage, bg=MainToolbarColor)
MainFrameExitButton.grid(column=1, row=0, padx=ButtonPadX, pady=ButtonPadY)

MainFrameEditButton = tk.Label(MainFrameToolbar, image=editButtonImage, bg=MainToolbarColor)
MainFrameEditButton.grid(column=2, row=0, padx=ButtonPadX, pady=ButtonPadY)

MainFrameTimeText = tk.StringVar()
MainFrameTimeLabel = tk.Label(MainFrameToolbar, textvariable=MainFrameTimeText, font=(MainFont, LargeFontSize),
                              fg=MainFrontColor, bg=MainToolbarColor)
MainFrameTimeLabel.grid(column=3, row=0, padx=LabelPadX, pady=LabelPadY, sticky=tk.E)

for column in range(3):
    MainFrameToolbar.grid_columnconfigure(column, weight=1)
MainFrameToolbar.grid_columnconfigure(3, weight=10)

# Create the other mainframe widgets
MainFrameAutoButton = tk.Label(MainFrame, text="Auto", font=(MainFont, LargeFontSize), image=offButtonImage,
                               compound=tk.BOTTOM, fg=MainFrontColor, bg=MainBackColor)
MainFrameAutoButton.grid(column=2, row=3)

MainFrameNightButton = tk.Label(MainFrame, image=nightButtonImage, bg=MainBackColor)
MainFrameNightButton.grid(column=0, row=3)

MainFrameDayButton = tk.Label(MainFrame, image=dayButtonImage, bg=MainBackColor)
MainFrameDayButton.grid(column=3, row=3)

MainFrameSkyButton = tk.Label(MainFrame, text="Sky", font=(MainFont, LargeFontSize), image=onButtonImage,
                              compound=tk.BOTTOM, fg=MainFrontColor, bg=MainBackColor)
MainFrameSkyButton.grid(column=1, row=3)

MainFrameProgressText = tk.StringVar()
MainFrameProgressLabel = tk.Label(MainFrame, textvariable=MainFrameProgressText, font=(MainFont, LargeFontSize),
                                  fg=MainFrontColor, bg=MainBackColor)
MainFrameProgressCanvasWidth = 796
MainFrameProgressCursorWidth = 32
MainFrameProgressCursorLimit = MainFrameProgressCanvasWidth - MainFrameProgressCursorWidth + 2
MainFrameProgressCanvas = tk.Canvas(MainFrame, bg=MainBackColor, height=30, width=MainFrameProgressCanvasWidth,
                                    highlightthickness=FieldBorderWidth)
MainFrameProgressRect = MainFrameProgressCanvas.create_rectangle(0, 0, MainFrameProgressCursorWidth,
                                                                 MainFrameProgressCursorWidth, fill=MainFrontColor,
                                                                 outline=MainBackColor)
MainFrameProgressLabel.grid(column=0, columnspan=4, row=1, pady=ButtonPadY)
MainFrameProgressCanvas.grid(column=0, columnspan=4, row=2, pady=ButtonPadY)

MainFrameSeparator1Canvas = tk.Canvas(MainFrame, bg=MainBackColor, height=0, width=MainFrameProgressCanvasWidth,
                                      highlightthickness=FieldBorderWidth)
MainFrameSeparator1Canvas.grid(column=0, columnspan=4, row=4)

MainFrameLightButton = []
# Find the name of the four buttons corresponding to Switch 0, Switch 1, Switch 2 and Switch 3 in light_list
# If any of them is not found, the corresponding button is given the name 'N/C'
for pos in range(4):
    try:
        work_light = next(light for light in light_list if 'switch' in light and light['switch'] == 'Switch ' + str(pos))
        button_name = work_light['name']
    except:
        button_name = 'N/C'
    MainFrameLightButton.append(tk.Label(MainFrame, text=button_name, font=(MainFont, LargeFontSize), image=offButtonImage,
                                compound=tk.BOTTOM, fg=MainFrontColor, bg=MainBackColor))
    MainFrameLightButton[-1].grid(column=pos, row=5)

MainFrameSeparator2Canvas = tk.Canvas(MainFrame, bg=MainBackColor, height=0, width=MainFrameProgressCanvasWidth, highlightthickness=FieldBorderWidth)
MainFrameSeparator2Canvas.grid(column=0, columnspan=4, row=6)

MainFrameVoltageText = tk.StringVar()
MainFrameVoltageLabel = tk.Label(MainFrame, textvariable=MainFrameVoltageText, font=(MainFont, LargeFontSize),
                                 fg=MainFrontColor, bg=MainBackColor)
MainFrameVoltageLabel.grid(column=0, row=7, sticky=tk.E)

MainFrameCurrentText = tk.StringVar()
MainFrameCurrentLabel = tk.Label(MainFrame, textvariable=MainFrameCurrentText, font=(MainFont, LargeFontSize),
                                 fg=MainFrontColor, bg=MainBackColor)
MainFrameCurrentLabel.grid(column=1, row=7, sticky=tk.E)

MainFramePowerText = tk.StringVar()
MainFramePowerLabel = tk.Label(MainFrame, textvariable=MainFramePowerText, font=(MainFont, LargeFontSize),
                               fg=MainFrontColor, bg=MainBackColor)
MainFramePowerLabel.grid(column=2, row=7, sticky=tk.E)

for column in range(4):
    MainFrame.grid_columnconfigure(column, minsize=200)

# Create tkinter ListFrame widgets
ListFrameBackButton = tk.Label(ListFrame, text='< Back', font=(MainFont, LargeFontSize), fg=ButtonFrontColor,
                               bg=ButtonBackColor)
ListFrameBackButton.grid(column=0, row=0, padx=ButtonPadX, pady=ButtonPadY, ipadx=10, sticky=tk.W)

ListFrameTestButton = tk.Label(ListFrame, text='Test', font=(MainFont, LargeFontSize), fg=ButtonFrontColor,
                               bg=ButtonBackColor)
ListFrameTestButton.grid(column=2, row=0, padx=ButtonPadX, pady=ButtonPadY, ipadx=10, sticky=tk.W)

ListFrameYScroll = tk.Scrollbar(ListFrame, orient=tk.VERTICAL, relief=tk.FLAT, troughcolor=ButtonBackColor, width=40)
ListFrameListbox = tk.Listbox(ListFrame, font=(MainFont, LargeFontSize), height=ListFrameListboxHeight,
                              yscrollcommand=ListFrameYScroll.set, activestyle='none',
                              bg=MainBackColor, fg=MainFrontColor, selectmode=tk.SINGLE,
                              selectbackground='light grey', selectforeground='black')
ListFrameYScroll['command'] = ListFrameListbox.yview
ListFrameListbox.grid(column=0, columnspan=3, row=2,
                      rowspan=ListFrameListboxHeight, padx=10, sticky=tk.W + tk.E)
ListFrameYScroll.grid(column=3, row=2, rowspan=ListFrameListboxHeight, sticky=tk.W + tk.N + tk.S)

ListFrameListboxContent = [d['name'] for d in light_list]
ListFrameListboxContent.sort()
ListFrameListbox.insert(1, *ListFrameListboxContent)
ListFrameListbox.selection_set(0)

for column in range(3):
    ListFrame.grid_columnconfigure(column, weight=6)
ListFrame.grid_columnconfigure(3, weight=1)


# Create tkinter TestFrame widgets
def TestFrameValuePadHandler(event):
    global TestFrameCurrentValue
    global TestFrameCurrentLight

    # event.x is the x position of the mouse in the canvas
    # TestFrame.grid_bbox()[2] is the width of the bounding box of the columns of the frame
    # In addition, two 20-pixel areas are reserved at the left and right of the canvas
    # for values 0 and 1000
    CanvasWidth = TestFrame.grid_bbox()[2] - FieldPadX * 2
    TestFrameCurrentValue = int((event.x - 20) * 1000 / (CanvasWidth - 40))

    if TestFrameCurrentValue < 0:
        TestFrameCurrentValue = 0
    elif TestFrameCurrentValue > 1000:
        TestFrameCurrentValue = 1000

    TestFrameValueField.configure(text=TestFrameCurrentValue)
    SetLEDBrightness(TestFrameCurrentLight, TestFrameCurrentValue)


TestFrameBackButton = tk.Label(TestFrame, text='< Back', font=(MainFont, LargeFontSize), bg=ButtonBackColor, fg=ButtonFrontColor)
TestFrameBackButton.grid(column=0, row=0, ipadx=10, padx=ButtonPadX, pady=ButtonPadY, sticky=tk.E + tk.S)

TestFrameNameLabel = tk.Label(TestFrame, text='Name', font=(MainFont, SmallFontSize), bg=MainBackColor, fg=MainFrontColor)
TestFrameNameLabel.grid(column=0, row=1, padx=LabelPadX, pady=LabelPadY, sticky=tk.W)

TestFrameNameField = tk.Label(TestFrame, font=(MainFont, LargeFontSize), fg=EditFrontColor, relief=tk.FLAT,
                              anchor=tk.W, bg=EditBackColor)
TestFrameNameField.grid(column=1, columnspan=3, row=1, padx=FieldPadX, pady=FieldPadY, sticky=tk.W + tk.E)

TestFrameModuleLabel = tk.Label(TestFrame, text='Module', font=(MainFont, SmallFontSize), bg=MainBackColor, fg=MainFrontColor)
TestFrameModuleLabel.grid(column=0, row=2, padx=LabelPadX, pady=LabelPadY, sticky=tk.W)

TestFrameModuleField = tk.Label(TestFrame, font=(MainFont, LargeFontSize), fg=EditFrontColor, relief=tk.FLAT,
                                anchor=tk.E, bg=EditBackColor)
TestFrameModuleField.grid(column=1, row=2, padx=FieldPadX, pady=FieldPadY, sticky=tk.W + tk.E)

TestFramePortLabel = tk.Label(TestFrame, text='Port', font=(MainFont, SmallFontSize), bg=MainBackColor, fg=MainFrontColor)
TestFramePortLabel.grid(column=2, row=2, padx=LabelPadX, pady=LabelPadY, sticky=tk.W)

TestFramePortField = tk.Label(TestFrame, font=(MainFont, LargeFontSize), fg=EditFrontColor, relief=tk.FLAT,
                              anchor=tk.E, bg=EditBackColor)
TestFramePortField.grid(column=3, row=2, padx=FieldPadX, pady=FieldPadY, sticky=tk.W + tk.E)

TestFrameValueLabel = tk.Label(TestFrame, text='Value', font=(MainFont, SmallFontSize), bg=MainBackColor, fg=MainFrontColor)
TestFrameValueLabel.grid(column=0, row=4, padx=LabelPadX, pady=LabelPadY, sticky=tk.W)

TestFrameValueField = tk.Label(TestFrame, font=(MainFont, LargeFontSize), fg=EditFrontColor, relief=tk.FLAT,
                               anchor=tk.E, bg=EditBackColor)
TestFrameValueField.grid(column=1, row=4, padx=FieldPadX, pady=FieldPadY, sticky=tk.W + tk.E)

TestFrameValuePad = tk.Canvas(TestFrame, bg=EditBackColor)
TestFrameValuePad.grid(column=0, row=5, columnspan=4, padx=FieldPadX, pady=FieldPadY, sticky=tk.W + tk.E)
TestFrameValuePad.bind('<Motion>', TestFrameValuePadHandler)

TestFrame.grid_columnconfigure(0, minsize=130)
TestFrame.grid_columnconfigure(1, minsize=268)
TestFrame.grid_columnconfigure(2, minsize=130)
TestFrame.grid_columnconfigure(3, minsize=268)

# List storing the current state of the four switches
switch_state = [False, False, False, False]


# Service function to toggle the lights attached to the four switches
def toggle_switch(switch):
    try:
        # Look for the lights where the switch parameter corresponds to the switch being toggled
        light_toggled = next(light for light in light_list if 'switch' in light and light['switch'] == 'Switch ' + chr(switch+48))
    except:
        return  # Exit function if there is no light with 'switch' == 'Switch X' in the list
    if switch_state[switch] is False:
        MainFrameLightButton[switch]["image"] = onButtonImage
        SetLEDBrightness(light_toggled, light_toggled['value_on'])
        switch_state[switch] = True
    else:
        MainFrameLightButton[switch]["image"] = offButtonImage
        SetLEDBrightness(light_toggled, light_toggled['value'])
        switch_state[switch] = False


def toggle_switch0(event=0):
    toggle_switch(0)


def toggle_switch1(event=0):
    toggle_switch(1)


def toggle_switch2(event=0):
    toggle_switch(2)


def toggle_switch3(event=0):
    toggle_switch(3)


# Define tkinter buttons and pads, and their event handlers
ButtonList = [
    {'Name': MainFrameExitButton, 'Handler': MainFrameExitButtonPressed},
    {'Name': MainFrameShutdownButton, 'Handler': MainFrameShutdownButtonPressed},
    {'Name': MainFrameEditButton, 'Handler': MainFrameEditButtonPressed},
    {'Name': MainFrameNightButton, 'Handler': go_to_night},
    {'Name': MainFrameSkyButton, 'Handler': MainFrameSkyButtonPressed},
    {'Name': MainFrameAutoButton, 'Handler': MainFrameAutoButtonPressed},
    {'Name': MainFrameDayButton, 'Handler': go_to_day},
    {'Name': MainFrameLightButton[0], 'Handler': toggle_switch0},
    {'Name': MainFrameLightButton[1], 'Handler': toggle_switch1},
    {'Name': MainFrameLightButton[2], 'Handler': toggle_switch2},
    {'Name': MainFrameLightButton[3], 'Handler': toggle_switch3},
    {'Name': ListFrameBackButton, 'Handler': ListFrameBackButtonPressed},
    {'Name': ListFrameTestButton, 'Handler': ListFrameTestButtonPressed},
    {'Name': TestFrameBackButton, 'Handler': TestFrameBackButtonPressed}]

# Register the button event handlers to tkinter widgets events
for Button in ButtonList:
    Button['Name'].bind("<Button>", Button['Handler'])


# Main loops
# Update all LEDs
def UpdateAllLEDs():
    if TestFrameActive is False:    # Update LEDs only if we are not in TestFrame
        now = time.perf_counter()
        # Compute the value of each LED
        for led in light_list:
            UpdateLED(now, led)
    if InSitu:
        # Send the command message to all LEDs on the SPI bus
        spi.writebytes(LEDCommand)
        # Send SkyLED data over serial comm to the Arduino controlling SkyLED
        # The command are
        # - "<FRRFGGFBBFWWBRRBGGBBBBWW>" to set front and back LEDs to the corresponding values.
        # - "<FRRFGGFBBFWWBRRBGGBBBBWW$" to store default values (used at startup) in EEPROM.
        # FRR, FGG, FBB, FWW, BRR, BGG, BBB and BWW are three-digit 12-bit hexadecimal numbers.
        SkyLEDMsg = '<'
        for v in SkyLEDColor:
            SkyLEDMsg = SkyLEDMsg + "%0.3X" % v
        SkyLEDMsg = SkyLEDMsg + '>'
        SkyLEDSerial.write(SkyLEDMsg.encode('utf-8'))
        # Debugging message:
        # print('Sent: ' + SkyLEDMsg)
    win.after(50, UpdateAllLEDs)   # Come back in 50 ms


# Update the day and night modes, automatically switching when in auto_day_night mode
dayNightUpdateCallbackID = 0


def dayNightUpdate():
    global dayNightUpdateCallbackID
    if auto_day_night:
        dayNightUpdateCallbackID = win.after(day_night_auto_period * 1000, dayNightUpdate)   # Come back after day_night_auto_period seconds
        if going_to_night:
            go_to_day()
        else:
            go_to_night()
    else:
        win.after_cancel(dayNightUpdateCallbackID)


# Display the time
def UpdateTimeDisplay():
    MainFrameTimeText.set(time.strftime('%I:%M%p'))
    win.after(1000, UpdateTimeDisplay)   # Come back in 1 s


# Display the LED voltage, power consumption and power
def UpdateVoltageDisplay():
    if InSitu is True and ina219Present is True:
        MainFrameVoltageText.set("{:2.1f} V".format(ina.supply_voltage()))
        try:
            MainFrameCurrentText.set("{:4.0f} mA".format(ina.current()))
            MainFramePowerText.set("{:3.1f} W".format(ina.power()/1000))
        except DeviceRangeError as e:
            # Current out of device range with specified shunt resistor
            MainFrameCurrentText.set("---- mA")
            MainFramePowerText.set("---- W")
        win.after(250, UpdateVoltageDisplay)   # Come back in 0.25 s
    else:
        MainFrameVoltageText.set("---- V")
        MainFrameCurrentText.set("---- mA")
        MainFramePowerText.set("---- W")


# Display the day/night progress bar
def UpdateProgressBar():
    now = time.perf_counter()
    progress_prct = (now-last_day_night_switch_time) / day_night_transition_length * 100
    if progress_prct > 100:
        progress_prct = 100
    if going_to_night:
        MainFrameDayButton["image"] = dayButtonImage
        MainFrameProgressCanvas.coords(MainFrameProgressRect,
                                       MainFrameProgressCursorLimit - progress_prct * MainFrameProgressCursorLimit / 100, 0,
                                       MainFrameProgressCursorLimit - progress_prct * MainFrameProgressCursorLimit / 100 +
                                       MainFrameProgressCursorWidth, MainFrameProgressCursorWidth)
        if progress_prct == 100:
            if auto_day_night:
                MainFrameProgressText.set("Night [{:.0f} / {:.0f} s]".format(now - last_day_night_switch_time - day_night_transition_length,
                                          day_night_auto_period - day_night_transition_length))
            else:
                MainFrameProgressText.set("Night [Paused]")
            MainFrameNightButton["image"] = nightOnButtonImage
        else:
            MainFrameProgressText.set("Sunset [{:.0f} / {:.0f} s]".format(now - last_day_night_switch_time, day_night_transition_length))
            # Flash the MainFrameNightButton (2 times per second)
            if int(now * 2) % 2 == 1:
                MainFrameNightButton["image"] = nightOnButtonImage
            else:
                MainFrameNightButton["image"] = nightButtonImage

    if going_to_day:
        MainFrameNightButton["image"] = nightButtonImage
        MainFrameProgressCanvas.coords(MainFrameProgressRect,
                                       progress_prct * MainFrameProgressCursorLimit / 100, 0,
                                       progress_prct * MainFrameProgressCursorLimit / 100 + MainFrameProgressCursorWidth,
                                       MainFrameProgressCursorWidth)
        if progress_prct == 100:
            if auto_day_night:
                MainFrameProgressText.set("Day [{:.0f} / {:.0f} s]".format(now - last_day_night_switch_time - day_night_transition_length,
                                          day_night_auto_period - day_night_transition_length))
            else:
                MainFrameProgressText.set("Day [Paused]")
            MainFrameDayButton["image"] = dayOnButtonImage
        else:
            MainFrameProgressText.set("Sunrise [{:.0f} / {:.0f} s]".format(now - last_day_night_switch_time, day_night_transition_length))
            # Flash the MainFrameDayButton (2 times per second)
            if int(now * 2) % 2 == 1:
                MainFrameDayButton["image"] = dayOnButtonImage
            else:
                MainFrameDayButton["image"] = dayButtonImage

    win.after(100, UpdateProgressBar)   # Come back in 100 ms


# Start loop update functions, then the main tkinter loop
InitConstantLEDs()                      # Called once
win.after(2000, StoreStartupSkyLED)     # Called once after 2 seconds in order to wait until the SkyLED Arduino has started
RandomizeDayNightTime()                 # Called once

UpdateAllLEDs()                         # Called repetitively using .after()
UpdateTimeDisplay()                     # Called repetitively using .after()
UpdateProgressBar()                     # Called repetitively using .after()
UpdateVoltageDisplay()                  # Called repetitively using .after()

MainFrame.tkraise()                     # Called once
if auto_day_night:
    # Start dayNightUpdate in day_night_auto_period seconds
    dayNightUpdateCallbackID = win.after(day_night_auto_period * 1000, dayNightUpdate)

win.mainloop()                          # Main tkinter event loop
