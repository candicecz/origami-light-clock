import busio
import adafruit_pcf8523
import time
import board
import adafruit_mpr121
import neopixel
import json
import random
import microcontroller

# I2C selection
myI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(myI2C)
touch_sensor = adafruit_mpr121.MPR121(myI2C)

CURRENT_DAY      = None
CURRENT_HOLIDAY  = None
CURRENT_HOUR     = None
COLOR_DAY        = None
COLOR_HOUR       = None

# ==================================
# TOUCH SENSORS
# ==================================
# Deals with touch sensor and their associated states.

# The maximum number of sensor inputs.
NUM_SENSOR_MAX = 12

# States and their corresponding sensor input index
POMODORO = 0

PRESENCE = 1
SAD      = 2
TIRED    = 4
ANGER    = 5
LOVE     = 6
FEAR     = 8
BUILDO   = 9

states = {
    "buildo": 0,
    "fear": 0,
    "love": 0,
    "presence": 0,
    "anger": 0,
    "sad": 0,
    "tired":0,
    "timestamp": None,
}

# Pomodoro clock management
POMO_ON = False # Is the Pomodoro clock on
POMO_START = 0  # unix timestamp of when the clock was started

# Pomodoro timer management
def start_pomodoro():
    global POMO_START
    global POMO_ON
    global COLOR_DAY
    global COLOR_HOUR
    global CURRENT_DAY
    global CURRENT_HOUR

    POMO_TIMER = 25 * 60 # Run time of pomo clock in seconds.
    while True:
        t = rtc.datetime

        # Change the color of the top pyramid according to the day.
        if (t.tm_wday != CURRENT_DAY):
            CURRENT_DAY = t.tm_wday
            COLOR_DAY = get_day_color(t.tm_wday)

            pyramid_top.fill(COLOR_DAY)
            pyramid_top.write()


        # Change the color of the bottom pyramid according to the hour.
        if(t.tm_hour != CURRENT_HOUR):
            CURRENT_HOUR = t.tm_hour
            COLOR_HOUR = get_hour_color(t.tm_hour)
            color_chase(pyramid_bottom, PYRAMID_LEN, COLOR_HOUR, 0.1)

        # Slowly pulse white when pomodoro timer is running.
        breathe(flower, FLOWER_LEN, WHITE, OFF, 1)
        # If the Pomodoro clock has elapsed, the flower does a rainbow light show.
        if time.mktime(t) > POMO_START + POMO_TIMER:
            wait = 0.05
            color_chase(flower, FLOWER_LEN, RED, wait)
            color_chase(flower, FLOWER_LEN, ORANGE, wait)
            color_chase(flower, FLOWER_LEN, YELLOW, wait)
            color_chase(flower, FLOWER_LEN, GREEN, wait)
            color_chase(flower, FLOWER_LEN, BLUE, wait)
            color_chase(flower, FLOWER_LEN, PURPLE, wait)
            time.sleep(1)
            break

        # If the user presses the pomodoro sensor while it is in use it toggles it off.
        if time.mktime(t) >= POMO_START + 1 and touch_sensor[POMODORO].value == True:
            break

    # Reset the state of things.
    POMO_ON = False
    POMO_START = 0
    return None

# The pomodoro clock.
def pomodoro_clock():
    global POMO_ON
    global POMO_START

    # Don't allow pomodoro to run when state is being set
    if states["timestamp"]:
        return None


    POMO_ON = True if POMO_ON == False else False
    if POMO_ON == True:
        t = rtc.datetime
        POMO_START = time.mktime(t)
        start_pomodoro()
    return None

# Update the state object with the user's input
def update_state_rank(state):
    # Set the unix time of the data input
    t = rtc.datetime

    states["timestamp"] = time.mktime(t)

    # Cycle through the ranks 0 to 5
    if(states[state] == 5):
        states[state] = 0
    else:
        states[state] = states[state] + 1

    # And fill the flower with the corresponsing state's color.
    flower.fill(get_color_for_state(state, states[state]))
    flower.write()

# Loop forever testing each input and printing when they're touched.
def monitor_sensors():
    # Loop through all 12 sensor inputs (0 - 11).
    for i in range(NUM_SENSOR_MAX):
        # If a sensor is touched, set the timestamp to the current time in unix.
        if touch_sensor[i].value:
            if i == BUILDO:
                update_state_rank("buildo")
            elif i == FEAR:
                update_state_rank("fear")
            elif i == LOVE:
                update_state_rank("love")
            elif i == PRESENCE:
                update_state_rank("presence")
            elif i == ANGER:
                update_state_rank("anger")
            elif i == SAD:
                update_state_rank("sad")
            elif i == TIRED:
                update_state_rank("tired")
            elif i == POMODORO:
                pomodoro_clock()

    time.sleep(0.25) # Small delay between touches.

# Handles writing the data to json file.
def write_data():
    # After a given time has elapsed, append the data to the json file.
    try:
        with open('data.json') as f:
            data = json.load(f)
        data.update({ states["timestamp"]: states})
        with open('data.json', 'w') as f:
            json.dump(data, f)

        # ... And reset the data object.
        return states.update({
            "buildo": 0,
            "fear": 0,
            "love": 0,
            "presence": 0,
            "anger": 0,
            "sad": 0,
            "tired":0,
            "timestamp": None,
        })
    # Error handling.
    except OSError as e:
        delay = 0.5

        # Blink 4 times if the storage is full
        if e.args[0] == 28:
            print("Storage is full.")
            delay = 0.25

        while True:
        # The flower neopixel will flash red in an error occurs.
            flower.fill(OFF)
            flower.write()
            time.sleep(delay)
            flower.fill(ERROR)
            flower.write()


# ==================================
#  NEOPIXELS
# ==================================

OFF    = (0, 0, 0)
ERROR  = (255, 0, 0)

# Colors for the DAY + TIME lights
WHITE          = (100, 100, 100)
LIGHTEST_GREEN = (50, 150, 50)
LIGHT_GREEN    = (65, 255, 0)
GREEN          = (30, 227, 33)
DARK_GREEN     = (19, 214, 65)
LIGHT_PINK     = (231, 84, 128)
PINK           = (255, 0, 179)
LIGHT_RED      = (245, 78, 114)
RED            = (245, 32, 32)
DARK_RED       = (100, 5, 5)
CYAN           = (29, 219, 197)
LIGHTEST_BLUE  = (132, 226, 245)
LIGHT_BLUE     = (5, 111, 240)
BLUE           = (85, 20, 250)
DARK_BLUE      = (19, 15, 255)
LILAC          = (91, 29, 110)
PURPLE         = (90, 2, 117)
LIGHT_VIOLET   = (132, 83, 230)
VIOLET         = (123, 5, 240)
FUSCHIA        = (223, 803, 205)
YELLOW         = (255, 223, 41)
MUSTARD        = (255, 139, 0)
LIGHT_ORANGE   = (219, 121, 29)
ORANGE         = (224, 87, 29)
DARK_ORANGE    = (255, 87, 3)

COLOR_ARRAY = (
    WHITE,
    LIGHTEST_GREEN,
    LIGHT_GREEN,
    GREEN,
    DARK_GREEN,
    LIGHT_PINK,
    PINK,
    LIGHT_RED,
    RED,
    DARK_RED,
    CYAN,
    LIGHTEST_BLUE,
    LIGHT_BLUE,
    BLUE,
    DARK_BLUE,
    LILAC,
    PURPLE,
    VIOLET,
    FUSCHIA,
    YELLOW,
    MUSTARD,
    LIGHT_ORANGE,
    ORANGE,
    DARK_ORANGE
)

# There are three light sections, the top(1) and bottom(2) pyramids as well as the center flower(3)
BRIGHTNESS_VALUE = 1
FLOWER_BRIGHTNESS_VALUE = 0.7

FLOWER_LEN = 16
flower = neopixel.NeoPixel(board.D10, FLOWER_LEN, pixel_order=neopixel.GRB, auto_write=False, brightness=FLOWER_BRIGHTNESS_VALUE)

PYRAMID_LEN = 14
pyramid_top = neopixel.NeoPixel(board.D5, PYRAMID_LEN, pixel_order=neopixel.GRB, auto_write=False, brightness=BRIGHTNESS_VALUE)
pyramid_bottom = neopixel.NeoPixel(board.D13, PYRAMID_LEN, pixel_order=neopixel.GRB, auto_write=False, brightness=BRIGHTNESS_VALUE)

# Start with all the lights off
flower.fill(OFF)
flower.write()

pyramid_top.fill(OFF)
pyramid_top.write()

pyramid_bottom.fill(OFF)
pyramid_bottom.write()


# Sets the colors for each state and increases the brightness based on the chosen rank.
def get_color_for_state(state, rank):
    rgb = (0, 0, 0)
    # Set color to off if no rank.
    if rank == 0:
        return rgb
    if state == "buildo":
        rgb = (44, 161, 35)
    elif state == "fear":
        rgb = (189, 15, 242)
    elif state == "love":
        rgb = (255, 41, 76)
    elif state == "presence":
        rgb = (235, 209, 16)
    elif state == "anger":
        rgb = (189, 0, 0)
    elif state == "sad":
        rgb = (4, 201, 126)
    elif state == "tired":
        rgb = (78, 38, 237)

    # The brightness of the light depends on the ranking of the state where 0 is off, 1 is low brightness and 5 is high.
    brightness = 5/rank
    new_rgb = [int(round(v)/brightness) for v in rgb]
    return new_rgb

# Light glows on and off slowly.
# I use for-loops to manage the sleep time here instead so that there is no bottle neck when
# a sensor is touched for example.
def breathe(light_unit, light_len, color_1, color_2, wait):
    for i in range(0, light_len):
        if(states["timestamp"]):
            return None

        if(True in touch_sensor.touched_pins):
            return None

        light_unit[i] = color_1
        time.sleep(0.1)
        light_unit.write()

    for i in range(0, wait):
        if(states["timestamp"]):
            break
        if(True in touch_sensor.touched_pins):
            break

        time.sleep(0.5)

    for i in range(0, light_len):
        if(states["timestamp"]):
            return None
        if(True in touch_sensor.touched_pins):
            return None
        light_unit[i] = color_2
        time.sleep(0.1)
        light_unit.write()

    for i in range(0, wait):
        if(states["timestamp"]):
            break

        if(True in touch_sensor.touched_pins):
            break

        time.sleep(0.5)
    return None


# Lights move in a circular fashion aroung the neopixel ring. The [wait] argument corresponds to the time between each pixel lighting up.
def color_chase(light_unit, light_len, color, wait):
    for i in range(light_len):
        if(states["timestamp"]):
            break
        if(True in touch_sensor.touched_pins):
            break

        light_unit[i] = color
        time.sleep(wait)
        light_unit.write()
    return None


def pick_rando_color():
    pick = random.randint(0, (len(COLOR_ARRAY)-1))
    rando_color = COLOR_ARRAY[pick]
    return rando_color


# ==================================
#  RESET TIME
# ==================================

# if False:   # change to True if you want to write the time!
#     #                     year, mon, date, hour, min, sec, wday, yday, isdst
#     t = time.struct_time((2020,  11,   28,   19,  20,  30,    6,   -1,    -1))
#     # you must set year, mon, date, hour, min, sec and weekday
#     # yearday is not supported, isdst can be set but we don't do anything with it at this time

#     print("Setting time to:", t)     # uncomment for debugging
#     rtc.datetime = t
#     print()

# ==================================
#  RUNNING THE CODE
# ==================================

# Returns a color based on the hour of the day
def get_hour_color(hour):
    if hour >= 0 and hour < 1:
        return MUSTARD
    elif hour >= 1 and hour < 8: # Shut off the lights during sleep time.
        return OFF
    elif hour >= 8 and hour < 9:
        return YELLOW
    elif hour >= 9 and hour < 10:
        return GREEN
    elif hour >= 10 and hour < 11:
        return LIGHT_RED
    elif hour >= 11 and hour < 12:
        return CYAN
    elif hour >= 12 and hour < 13:
        return BLUE
    elif hour >= 13 and hour < 14:
        return FUSCHIA
    elif hour >= 14 and hour < 15:
        return LIGHT_ORANGE
    elif hour >= 15 and hour < 16:
        return RED
    elif hour >= 16 and hour < 17:
        return LIGHT_BLUE
    elif hour >= 17 and hour < 18:
        return LIGHT_GREEN
    elif hour >= 18 and hour < 19:
        return DARK_ORANGE
    elif hour >= 19 and hour < 20:
        return PINK
    elif hour >= 20 and hour < 21:
        return VIOLET
    elif hour >= 21 and hour < 22:
        return DARK_BLUE
    elif hour >= 22 and hour < 23:
        return DARK_RED
    elif hour >= 23 and hour < 24:
        return DARK_GREEN

    return OFF

# Returns a color based on the day.
def get_day_color(day):
    if day == 0: # Sunday
        return LIGHTEST_BLUE
    elif day == 1:
        return YELLOW
    elif day == 2:
       return ORANGE
    elif day == 3:
        return LILAC
    elif day == 4:
        return LIGHTEST_GREEN
    elif day == 5:
        return LIGHT_VIOLET
    elif day == 6:
        return LIGHT_PINK
    return OFF

while True:

    t = rtc.datetime

    if t.tm_hour >= 1 and t.tm_hour < 8: # 1a to 8a, you should be sleeping. Reset.
        pyramid_top.fill(OFF)
        pyramid_top.write()
        pyramid_bottom.fill(OFF)
        pyramid_bottom.write()
        flower.fill(OFF)
        flower.write()
        CURRENT_DAY  = None
        CURRENT_HOUR = None
        COLOR_DAY    = None
        COLOR_HOUR   = None
        continue
        
    # Detect whether a sensor has been touched and register the corresponding data during waking hours.
    if (True in touch_sensor.touched_pins) and not (t.tm_hour >= 1 and t.tm_hour < 8):
        monitor_sensors()
        continue

    # If the data has changed in anyway we detect whether the desired time has elapsed
    if states["timestamp"] and (time.mktime(t) - states["timestamp"] >= 30):
        write_data()
        continue

    # Change the color of the top pyramid according to the day.
    if (t.tm_wday != CURRENT_DAY):
        CURRENT_DAY = t.tm_wday
        COLOR_DAY = get_day_color(t.tm_wday)
        if (t.tm_mon == 12 and t.tm_mday == 25): # Christmas
            CURRENT_HOLIDAY = "CHRISTMAS"
        elif (t.tm_mon == 1 and t.tm_mday == 1): # New Year's Day
            CURRENT_HOLIDAY = "NEW YEAR"
        elif (t.tm_mon == 2 and t.tm_mday == 14): # Valentine's Day
            CURRENT_HOLIDAY = "VALENTINE"
        elif (t.tm_mon == 5 and t.tm_mday == 18): # Plant Day
            CURRENT_HOLIDAY = "PLANT"
        elif (t.tm_mon == 9 and t.tm_mday == 2) or (t.tm_mon == 10 and t.tm_mday == 19) or (t.tm_mon == 10 and t.tm_mday == 22) or (t.tm_mon == 1 and t.tm_mday == 6): # Other significant days
            CURRENT_HOLIDAY = "OTHER"
        elif (t.tm_mon == 10 and t.tm_mday == 31): # Halloween Day
            CURRENT_HOLIDAY = "HALLOWEEN"
        else:
            CURRENT_HOLIDAY = None

        pyramid_top.fill(COLOR_DAY)
        pyramid_top.write()
        time.sleep(0.5)
        continue


    # Change the color of the bottom pyramid according to the hour.
    if (t.tm_hour != CURRENT_HOUR):
        CURRENT_HOUR = t.tm_hour
        COLOR_HOUR   = get_hour_color(t.tm_hour)
        color_chase(pyramid_bottom, PYRAMID_LEN, COLOR_HOUR, 0.1)
        time.sleep(0.5)
        continue


    # Flower cycles between both day and hour colors  when Pomodoro is not on and the state isn't being set.
    if (COLOR_DAY and COLOR_HOUR) and not POMO_ON and not states["timestamp"]:
        # Different center flower colors for the holiday and special days.
        if CURRENT_HOLIDAY is not None: # Christmas
            if (CURRENT_HOLIDAY == "CHRISTMAS"):
                breathe(flower, FLOWER_LEN, GREEN, RED, 1)
            elif (CURRENT_HOLIDAY == "NEW YEAR"):
                wait = 0.05
                color_1 = pick_rando_color()
                color_2 = pick_rando_color()
                color_chase(flower, FLOWER_LEN, color_1, wait)
                color_chase(flower, FLOWER_LEN, color_2, wait)
            elif (CURRENT_HOLIDAY == "VALENTINE"):
                breathe(flower, FLOWER_LEN, PINK, RED, 1)
            elif (CURRENT_HOLIDAY == "PLANT"):
                breathe(flower, FLOWER_LEN, GREEN, LIGHT_GREEN, 1)
            elif (CURRENT_HOLIDAY == "OTHER"):   
                wait = 0.05
                color_1 = pick_rando_color()
                color_2 = pick_rando_color()
                breathe(flower, FLOWER_LEN, color_1, color_2, 1)
            elif (CURRENT_HOLIDAY == "HALLOWEEN"): # Halloween Day
                breathe(flower, FLOWER_LEN, LIGHT_ORANGE, DARK_ORANGE, 1)
        else:
            breathe(flower, FLOWER_LEN, COLOR_DAY, COLOR_HOUR, 1)
        continue

    time.sleep(0.25)