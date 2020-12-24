# CHRIS' MAD CHRISTMAS CLOCK

My first electronics build! Inspired by Charlyn's clock https://charlyn.codes/ac-nova-light-clock/

Components:

- 4 neopixel RGB jewels (7pixels each) (2 in each pyramid zone)
- 1 16pixel RGB ring
- 1 feather micro-controller + featherwing
- RTC clock module
- 12 key capacitive touch sensor breakout board
- Libraries courtesy of Circuit Python
  [ * all hardware bought from DIGI-KEY ]

## What is this thing

The goal of this clock is for a, decoration, of course and b, as a means for Chris to log the states that he wanted to log throughout his day.

Chris can cycle through a variety of predetermined states and their associated colours.

```
[YELLOW     = "Presence" ]
[GREEN      = "Buildo"   ] i.e. productivity/growth
[RED        = "Anger"    ]
[PURPLE     = "Fear"     ]
[DARK BLUE  = "Tiredness"]
[LIGHT BLUE = "Sadness"  ]
[PINK       = "Love"  ]
```

Each tap corresponds to a rank(from 1 to 5). The light at the center will have an increasing brightness to indicated this cycle.

There is also a pomodoro clock that can be activated by pressing the flower to the right of the center light. The pomodoro clock will work for 25 minutes after which, a rainbow light show will display in the center to indicate that the time has elapsed. It will then return to the default mode. Note that the pomodoro clock can be toggled off at any point by pressing the same flower that was used to activate it.

Overall, this project contains 3 light zones.
The top displays a colour for the day of the week.
The bottom displays a colour for the hour of the day.
The center glows between the former two colors. - Once special days it loops through random colors. - On holidays, it loops through colors that denote that holiday (i.e. red and green for christmas)

## Install

To run, simply drop all the files + the appropriate circuit python libraries in the micro-controller root. To collect the data, you must enter read-only mode (instructions below).

## Retrieving the data

The data that Chris enters will be recorded in a JSON file at the root directory. To retrieve the data just connect the micro-controller with a data usb-a micro-b cable (make sure it has a data-line). The data object will contain a 1-5 ranking for each state and the timestamp for when the data is recorded. Unset states will default to 0, which for our purposes means null.

Later we will have the possibility of making a very cool data viz summing up all Chris' states.

** IMPORTANT TO NOTE **

Circuit python only allows us to read OR write at one time, so when in read-only mode(which is the setting that allows the micro-controller to run the code AND write to the json file) we CANNOT edit the code in the editor. Therefore there is some info in the `boot.py` as well as below about how to go in and out of these states.

Additional information can also be found here:
https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage

## Going into read-mode

For when you want to register the data.

1. Set the following as your `boot.py`.

```python
    import storage

    storage.remount("/", False)
```

2. Press the `reset` button on the micro-controller. That's it.

## Going into write-mode

For when you want to edit the code.

1. Open the REPL (I used the Mu code editor)
2. Run the following:

```
    >>> import os
    >>> os.listdir("/")
    >>> os.rename("/boot.py", "/boot.bak")
```

3. Press the `reset` button on the micro-controller.

## Parsing the data

The data is stored in `data.json` at the root.

```
The general format is :
{
    timestamp: {
        anger: 0,
        sad: 0,
        buildo: 0,
        tired: 0,
        presence: 0,
        love: 0,
        fear: 0
    }
}

```

The time is set using the rtc clock module and python's time library: https://circuitpython.readthedocs.io/en/latest/shared-bindings/time/#time.mktime

To convert the timestamp in JavaScript:

```JavaScript
new Date(1608677325 * 1000) /* JS counts in ms*/
// Tue Dec 22 2020 17:48:45 GMT-0500 (GMT-05:00)

/* and to get that timezone. */
new Date(1608677325 *1000).getTimezoneOffset()/60
// 5
```
