###############################################
# Set LED parameters
# mode: Cycle: Continuously cycle through the 'time'/'value' sequence. Both sequences must have the same number of elements.
#       Day/Night: Go through the 'to_night' or 'to_day' sequence then hold the last value.
#       Random Day/Night: Switch, at a random time, between 'value_day' during the day and 'value_night' during the night.
#       Constant: Constant value at 'value', possibly change to 'value_on' using a switch.
# time: list of sequence event times (in seconds)
# value: list of sequence event values (0-1000) corresponding to event times
# switch: if 'Sky', 'Switch 0', 'Switch 1', 'Switch 2', 'Switch 3', light controlled by the corresponding switch
# module: address of the TLC59711 module, from 0. SkyLEDModule (= 100) is reserved for SkyLED LEDs 
# port: port of the corresponding PWM output, 0 to 11

SkyLEDModule = 100
light_list = [
    {'name': 'U/G left',      'mode': 'Constant', 'value': 0, 'value_on': 1000, 'switch': 'Switch 0', 'module': 0, 'port': 6},
    {'name': 'U/G left back', 'mode': 'Constant', 'value': 0, 'value_on': 1000, 'switch': 'Switch 1', 'module': 14, 'port': 2},
    {'name': 'U/G right',     'mode': 'Constant', 'value': 0, 'value_on': 1000, 'switch': 'Switch 3', 'module': 6, 'port': 11},

    {'name': 'Sky front red',   'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0, 200, 100,  0], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [  0,   0,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 0},
    {'name': 'Sky front green', 'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0, 100, 100,  0], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [  0,   0,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 1},
    {'name': 'Sky front blue',  'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0,   0,  60, 80], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [ 80,  60,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 2},
    {'name': 'Sky front white', 'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [1000, 100, 100, 40], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [ 40, 100, 350, 1000], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 3},

    {'name': 'Sky back red',   'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0, 400, 200,   0], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [  0,   0,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 4},
    {'name': 'Sky back green', 'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0, 100, 100,   0], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [  0,   0,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 5},
    {'name': 'Sky back blue',  'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [   0,   0,  60, 300], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [300,  60,   0,    0], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 6},
    {'name': 'Sky back white', 'mode': 'Day/Night', 'time_to_night': [0,  20,  40,  60], 'value_to_night': [1000, 100, 100,  40], 'time_to_day': [0,  20,  40,  60], 'value_to_day':  [ 40, 100, 350, 1000], 'switch': 'Sky', 'module': SkyLEDModule, 'port': 7},

    {'name': 'Tower 1 red warning',  'mode': 'Cycle', 'time': [0.0, 2.0, 2.3, 2.7, 3.0], 'value': [300, 300, 0, 0, 300], 'module': 0, 'port': 4},
    {'name': 'Tower 1 night',        'mode': 'Random Day/Night', 'value_night': 300, 'value_day': 0, 'module': 0, 'port': 5},
    {'name': 'Tower 2 red warning',  'mode': 'Cycle', 'time': [0.0, 1.9, 2.2, 2.6, 2.9], 'value': [300, 300, 0, 0, 300], 'module': 14, 'port': 0},
    {'name': 'Tower 2 night',        'mode': 'Random Day/Night', 'value_night': 300, 'value_day': 0, 'module': 14, 'port': 1},

    {'name': 'Shin-Yukari control tower',           'mode': 'Constant', 'value':  100, 'module': 2, 'port': 0},
    {'name': 'Shin-Yukari track 2 light',           'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 1},
    {'name': 'Parking ceiling light 5 (top left)',  'mode': 'Constant', 'value':  300, 'module': 2, 'port': 2},
    {'name': 'Parking ceiling light 6 (top right)', 'mode': 'Constant', 'value':  300, 'module': 2, 'port': 3},
    {'name': 'Shin-Yukari track 4 light',           'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 4},
    {'name': 'Shin-Yukari track 1-2 centre',        'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 5},
    {'name': 'Shin-Yukari track 3-4 centre',        'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 6},
    {'name': 'Shin-Yukari track 3 light',           'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 7},
    {'name': 'Shin-Yukari track 2 light',           'mode': 'Constant', 'value': 1000, 'module': 2, 'port': 8},
    {'name': 'Shin-Yukari south lamp posts', 'mode': 'Random Day/Night', 'value_night': 500, 'value_day': 0, 'module': 2, 'port': 11},
    {'name': 'Shin-Yukari south blue trees', 'mode': 'Random Day/Night', 'value_night': 500, 'value_day': 0, 'module': 2, 'port': 10},

    {'name': 'Shin-Yukari station north ceiling',                    'mode': 'Constant', 'value': 200, 'module': 4, 'port': 0},
    {'name': 'Shin-Yukari station south ceiling',                    'mode': 'Constant', 'value': 200, 'module': 4, 'port': 2},
    {'name': 'Shin-Yukari station ceiling indications',              'mode': 'Constant', 'value': 200, 'module': 4, 'port': 1},
    {'name': 'Shin-Yukari station ad boards',                        'mode': 'Constant', 'value': 200, 'module': 4, 'port': 3},
    {'name': 'Shin-Yukari station Uniqlo window',                    'mode': 'Constant', 'value': 200, 'module': 4, 'port': 4},
    {'name': 'Shin-Yukari station Uniqlo JTB ceiling',               'mode': 'Constant', 'value': 200, 'module': 4, 'port': 5},
    {'name': 'Shin-Yukari station JTB logo',                         'mode': 'Constant', 'value': 200, 'module': 4, 'port': 6},
    {'name': 'Shin-Yukari station Yoshinoya 7-11 ceiling',           'mode': 'Constant', 'value': 200, 'module': 4, 'port': 7},
    {'name': 'Shin-Yukari station Yoshinoya 7-11 logo',              'mode': 'Constant', 'value': 200, 'module': 4, 'port': 8},
    {'name': 'Shin-Yukari station Starbucks room pendant lights',    'mode': 'Constant', 'value':  60, 'module': 5, 'port': 0},
    {'name': 'Shin-Yukari station Starbucks counter pendant lights', 'mode': 'Constant', 'value':  60, 'module': 5, 'port': 1},
    {'name': 'Shin-Yukari station lockers',                          'mode': 'Constant', 'value': 200, 'module': 5, 'port': 2},
    {'name': 'Shin-Yukari station Cafe de Crie',                     'mode': 'Constant', 'value': 200, 'module': 5, 'port': 3},
    {'name': 'Shin-Yukari station Starbucks ceiling',                'mode': 'Constant', 'value': 200, 'module': 5, 'port': 4},
    {'name': 'Shin-Yukari station outdoor left',                     'mode': 'Constant', 'value': 200, 'module': 5, 'port': 9},
    {'name': 'Shin-Yukari station outdoor taxi stand',               'mode': 'Constant', 'value': 200, 'module': 5, 'port': 10},
    {'name': 'Shin-Yukari station outdoor right',                    'mode': 'Constant', 'value': 200, 'module': 5, 'port': 11},

    {'name': 'Tram station track 1',             'mode': 'Constant', 'value': 200, 'module': 3, 'port': 0},
    {'name': 'Tram station track 2',             'mode': 'Day/Night', 'time_to_night': [0, 6.0, 6.1, 6.2, 6.3, 60], 'value_to_night': [0, 0, 200, 0, 200, 200], 'time_to_day': [0, 45, 45.2, 60], 'value_to_day': [200, 200, 0, 0], 'module': 3, 'port': 1},
    {'name': 'Tram station track 3',             'mode': 'Day/Night', 'time_to_night': [0, 7.0, 7.1, 7.2, 7.3, 60], 'value_to_night': [0, 0, 200, 0, 200, 200], 'time_to_day': [0, 45, 45.2, 60], 'value_to_day': [200, 200, 0, 0], 'module': 3, 'port': 2},
    {'name': 'Tram station vending machines',    'mode': 'Constant', 'value': 200, 'module': 3, 'port': 3},
    {'name': 'Tram station red stop signals',    'mode': 'Constant', 'value': 50, 'module': 3, 'port': 4},

    {'name': 'Shin-Yukari tunnel east 1', 'mode': 'Constant', 'value': 60, 'module': 3, 'port': 6},
    {'name': 'Shin-Yukari tunnel east 2', 'mode': 'Constant', 'value': 60, 'module': 3, 'port': 7},
    {'name': 'Shin-Yukari tunnel east 3', 'mode': 'Constant', 'value': 42, 'module': 6, 'port': 6},

    {'name': 'Truck terminal lamp posts 1',      'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 6, 'port': 9},
    {'name': 'Truck terminal lamp posts 2',      'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 6, 'port': 10},
    {'name': 'Truck terminal lamp posts 3',      'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 6, 'port': 11},
    {'name': 'Truck terminal loading bay light', 'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 6, 'port': 7},
    {'name': 'Truck terminal ceiling light',     'mode': 'Constant', 'value': 100, 'module': 6, 'port': 8},

    {'name': 'Maintenance office staircase',          'mode': 'Constant', 'value': 300, 'module': 6, 'port': 2},
    {'name': 'Maintenance office parking lamp posts', 'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 6, 'port': 4},
    {'name': 'Maintenance office 1Fl entrance',       'mode': 'Constant', 'value': 100, 'module': 6, 'port': 0},
    {'name': 'Maintenance office 1Fl room',           'mode': 'Cycle', 'time': [0, 46.0, 46.1, 46.2, 46.4, 46.5, 46.6, 80], 'value': [0, 0, 150, 0, 150, 0, 150, 150], 'module': 6, 'port': 1},
    {'name': 'Maintenance office 2Fl Meeting Room',   'mode': 'Constant', 'value': 100, 'module': 6, 'port': 5},
    {'name': 'Maintenance office 3Fl Room',           'mode': 'Constant', 'value': 120, 'module': 6, 'port': 3},

    {'name': 'Engine house lamp posts',      'mode': 'Random Day/Night', 'value_night': 100, 'value_day': 0, 'module': 9, 'port': 6},
    {'name': 'Engine house yard spotlights', 'mode': 'Random Day/Night', 'value_night': 200, 'value_day': 0, 'module': 9, 'port': 7},
    {'name': 'Engine house indoor lights',   'mode': 'Random Day/Night', 'value_night': 300, 'value_day': 100, 'module': 9, 'port': 8},

    {'name': 'Yukari Hill temple lamp posts', 'mode': 'Random Day/Night', 'value_night': 100, 'value_day': 0, 'module': 9, 'port': 4},
    {'name': 'Yukari Hill pagoda facade',     'mode': 'Random Day/Night', 'value_night': 1000, 'value_day': 0, 'module': 9, 'port': 3},
    {'name': 'Yukari Hill temple facade',     'mode': 'Random Day/Night', 'value_night': 500, 'value_day': 200, 'module': 9, 'port': 5},
    {'name': 'Yukari Hill tunnel',            'mode': 'Constant', 'value': 150, 'module': 9, 'port': 0},

    {'name': 'Japanese restaurant parking exit',     'mode': 'Constant', 'value': 200, 'module': 14, 'port': 8},
    {'name': 'Japanese restaurant parking entrance', 'mode': 'Constant', 'value': 200, 'module': 14, 'port': 11},
    {'name': 'Japanese restaurant indoor front',     'mode': 'Constant', 'value': 200, 'module': 14, 'port': 10},
    {'name': 'Japanese restaurant indoor back',      'mode': 'Cycle', 'time': [0.0, 20.0, 20.1, 23.0], 'value': [150, 150, 0, 0], 'module': 14, 'port': 9},
    {'name': 'Japanese restaurant entrance sign',    'mode': 'Cycle', 'time': [0.0, 0.5, 0.51, 1.0], 'value': [300, 300, 0, 0], 'module': 14, 'port': 7},

    {'name': 'Parking ceiling light 1', 'mode': 'Constant', 'value': 250, 'module': 1, 'port': 2},
    {'name': 'Parking ceiling light 2', 'mode': 'Constant', 'value': 250, 'module': 1, 'port': 3},
    {'name': 'Parking ceiling light 3', 'mode': 'Constant', 'value': 250, 'module': 1, 'port': 4},
    {'name': 'Parking ceiling light 4', 'mode': 'Constant', 'value': 250, 'module': 1, 'port': 5},
    {'name': 'Parking lift tower', 'mode': 'Constant', 'value': 300, 'module': 1, 'port': 6},
    {'name': 'Parking car 1 (north roof) + car 3 (entrance)', 'mode': 'Constant', 'value': 200, 'module': 1, 'port': 0},
    {'name': 'Parking car 2', 'mode': 'Cycle', 'time': [0.0, 30.0, 30.01, 35.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 1},
    {'name': 'Parking car 4', 'mode': 'Cycle', 'time': [0.0, 34.0, 34.01, 40.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 7},
    {'name': 'Parking car 5', 'mode': 'Cycle', 'time': [0.0, 35.0, 35.01, 45.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 8},
    {'name': 'Parking car 6', 'mode': 'Cycle', 'time': [0.0, 22.0, 22.01, 25.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 9},
    {'name': 'Parking car 7', 'mode': 'Cycle', 'time': [0.0, 27.0, 27.01, 33.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 10},
    {'name': 'Parking car 8', 'mode': 'Cycle', 'time': [0.0, 38.0, 38.01, 41.0], 'value': [100, 100, 0, 0], 'module': 1, 'port': 11}]