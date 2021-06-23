#!/usr/bin/python3
from sense_hat import SenseHat
from datetime import datetime
import time
import pyowm
import socket
import requests

# Sensehat Parameters
sense = SenseHat()
sense.set_rotation(180)

# Sensehat Color Codes
def brightness(b):
    global white, red, green, blue, pink, yellow, purple, speed
    white = (b,b,b)
    red = (b,0,0)
    green = (0,b,0)
    blue = (0,0,b)
    pink = (b,0,b)
    yellow = (b,b,0)
    purple = (0,b,b)
    speed = 0.04

# Sense Output Function
def sensehat(mess,color):
    sense.show_message(mess,text_colour=color,scroll_speed=speed)

# OWM parameters
owm = pyowm.OWM('84d996853fcc4db149bc40acb09a3ef7')
mgr = owm.weather_manager()

# Check Internet connectivity
def is_connected():
  try:
    host = socket.gethostbyname("www.google.com")
    s = socket.create_connection((host, 80), 2)
    return True
  except:
    return False

# Get Time
def print_time():
    global time_data
    now = datetime.now()
    time_data = now.strftime("%I:%M%p")

# Get OWM Weather Data
def get_owm_data():
    global temp, feel, wind, status, obs_time, sun_rise, sun_set
    observation = mgr.weather_at_coords(53.26,-6.21)
    #print("API Call Executed now")
    w = observation.weather

    # Parse Weather Data
    temp = str(round(w.temperature('celsius')['temp']))
    feel = str(round(w.temperature('celsius')['feels_like']))
    wind = str(round(w.wind("km_hour")['speed']))
    status = w.detailed_status.title()
    obs_time = observation.reception_time()
    sun_rise = time.gmtime(w.sunrise_time())
    sun_set = time.gmtime(w.sunset_time())

def populate():
    global irl_cases, cases_in, cases_pb, cases_kpt, pop_time

    # Ireland Data
    try:
        irl_data = requests.get('https://coronavirus-19-api.herokuapp.com/countries/ireland')
        irl_cases = str(irl_data.json()['todayCases'])
        irl_data.close()
    except:
        irl_cases = str(0)

    # Print India/Punjab Data
    try:
        res_in = requests.get(url='https://api.covid19india.org/data.json')
        data_in = res_in.json()
        res_in.close()
        for m in data_in['statewise']:
            if m['state'] == 'Total':
                cases_in = str(m['deltaconfirmed'])
            if m['state'] == 'Punjab':
                cases_pb = str(m['deltaconfirmed'])
    except:
        cases_in = str(0)
        cases_pb = str(0)

    # Kapurthala
    try:
        res_dist = requests.get(url='https://api.covid19india.org/state_district_wise.json')
        data_dist = res_dist.json()
        res_dist.close()
        cases_kpt = str(data_dist['Punjab']['districtData']['Kapurthala']['delta']['confirmed'])
    except:
        cases_kpt = str(0)


obs_time = 0
pop_time = 0

#time.time() - obs_time
#time.time() - pop_time

populate()

sun_rise = time.gmtime()
sun_set = time.gmtime()

def weather_main():
    while True:
        if time.gmtime() >= sun_rise:
            if time.gmtime() >= sun_set:
                bright_ness = 50
            else:
                bright_ness = 200
            brightness(bright_ness)

            print_time()
            inside_temp = str(round(sense.temp))

            if is_connected():
                # Fetch fresh weather data after every 5 minutes
                if (time.time() - obs_time) > 300:
                    try:
                        get_owm_data()
                        #print("Ran API Function", time.time(), obs_time, time_data )
                    except Exception as e:
                        #print(str(e))
                        sensehat("Error: " + str(e), blue)

                #print(time.time() - obs_time, temp,feel,wind,status)
                # Print the Data
                sensehat(time_data, purple)
                try:
                    sensehat(status.title(), yellow)
                    sensehat("In: " + inside_temp + "'C", green)
                    sensehat("Out: " + temp + "'C", red)
                    sensehat("Feels: " + feel + "'C", blue)
                    sensehat("Wind: " + wind + "km/h", pink)
                except NameError:
                    pass

                # Fetch fresh Covid Data after every 5 minutes
                if (time.time() - pop_time) > 300:
                    populate()

                if irl_cases != '0':
                    sensehat("Irl: " + irl_cases, red)
                if cases_in != '0':
                    sensehat("In: " + cases_in, red)
                if cases_pb != '0':
                    sensehat("Pb: " + cases_pb, red)
                if cases_kpt != '0':
                    sensehat("Kpt: " + cases_kpt, red)
                #print(time.time() - pop_time, cases)

            else:
                inside_humidity = str(round(sense.humidity))
                sensehat("Time: " + time_data, white)
                sensehat("In: " + inside_temp  + "\'C", green)
                sensehat("Hum: In: " + inside_humidity + "%", pink)
        else:
            time.sleep(60)
            pass

if __name__ == "__main__":
    weather_main()
