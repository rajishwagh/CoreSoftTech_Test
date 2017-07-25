'''
Created on Jul 24, 2017

@author: rjw0028
Python 2.7.2
pymongo 3.4.0
'''

'''
--------------------Requirements--------------------
This code needs a few things to be in place before it can be run.
1. Mongod must be instantiated
2. File named 'cities.ini' should be present in "C:\"
3. Format of this file must be: 
[cities]
'auburn' : '4830796'            --> <cityname> : <city id according to http://openweathermap.org/help/city_list.txt>
'london' : '2643741'
'mumbai' : '1275339'
...

What the program does:

        This program, requests, openweather.com to send data about weather foecast every 2 hours on two separate threads using API access keys.
        It uses another thread to save urls pointing to 256x256 png images of weather maps from the same website using API access keys.
        This data is stored in data base mongo db as JSON files.
        Another thread, re-reads the config file called: cities.ini every 30 seconds
        This file contains information about which locations to be monitored. All the above three threads use this file and
        download info about the given cities
        The last thread, uses the saved data from the maps mongo db collection and downloads the latest weather map. 
        Then displays it for 5 minutes and closes the image to display another latest weather map image.

Note:-

        I studied about pymongo and mongoDB before starting and tested the code...
        The code seemed to work perfectly then. I was able to import Connection from the pymongo module.
        However, as I came to the end of the program, due to some reason, the module did not want to get imported.
        For that reason I have not run this program all together. I have tested/ran all of its smaller parts separately.
        I hope it works.

'''
import datetime, time, random, json, urllib, threading, time, ConfigParser, gridfs
from pymongo import Connection
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
API_KEYS_LIST = ['626065bef7e7c8883ff84245fafffa86', '9b19df8174a6d64f5e11b01ecd7d7040', '677d1ff040e3b35576cd904925955d40']
Freezing_Temp = 2.0
Confg = ConfigParser.ConfigParser()
City_List = [] # [['auburn', '7654632'],['london','5482749'],['mumbai','5482994']]
IMG_ID = {} # {{<Image ID1>: <timestamp1>},{<Image ID2>: <timestamp2>}}
conIn = Connection()    # Instance of a connection. This assumes that an instance of mongod is active on Windows cmd prompt.
pymondb = conIn.weather_data    # database name is weather_data... and variable handling it is pymondb
forecast1 = pymondb.fore5d3h    # collection name is fore5d3h... and variable handling it is forecast1
forecast2 = pymondb.fore16dd    # collection name is fore16dd... and variable handling it is forecast2
foremaps = pymondb.maps         # collection name if maps... and variable handling it is foremaps
Alerts_Dict = {}

gfs = gridfs.GridFS(pymondb)

class myThread (threading.Thread):
    def __init__(self, threadID, name_):
        global thread_num
        thread_num += 1
        self.threadID = threadID
        self.name_ = name_
    def cnfg_refresh(self):     # Seperate thread to just run the reloading of config file... Requires a file called cities to be present in C:\
        global Confg, City_List
        City_List = []  # [['auburn', '7654632'],['london','5482749'],['mumbai','5482994']]
        while True: 
            print "Running thread: ", self.threadID, " named: ", self.name_
            Confg.read("c:\\cities.ini")
            Sects = Confg.sections()
            Citst = Confg.options(Sects[0]) # options
            for city in Citst:
                City_List.append([str(city), str(Confg.get(Sects[0], city))])    # This should give us the city ID
            time.sleep(30)
    def D_5_3(self):
        global City_List, API_KEYS_LIST, forecast1
        self.Insertion_ids = []
        self.type = 'D_5_3'     # type defined to use the same functions of get_url and Alerts
        self.API_key = random.choice(API_KEYS_LIST)
        st = time.time()
        while True:
            print "Running thread: ", self.threadID, " named: ", self.name_
            for city in City_List:
                url = get_url(city[1], self.API_key, self.type, None, None, None)
                data_dict = update_data_dict(url)
                
                t_id = forecast1.insert_one(data_dict)
                self.Insertion_ids.append(t_id.inserted_id())
                for l in data_dict.get('list'):   
                    Alerts(self.type, l)   # Checking for alerts in each data set and the function will save appropriate text.
                    
            time.sleep((2.0*3600) - (time.time() - st)) # Delay of 2 hours according to the permissions of the API
            st = time.time()

    def D_16_24(self):
        global City_List, API_KEYS_LIST, forecast2
        self.Insertion_ids = []
        self.type = 'D_16_24'     # type defined to use the same functions of get_url and Alerts
        self.API_key = random.choice(API_KEYS_LIST)
        st = time.time()
        while True:
            print "Running thread: ", self.threadID, " named: ", self.name_
            for city in City_List:
                url = get_url(city[1], self.API_key, self.type, None, None, None)
                data_dict = update_data_dict(url)
                
                t_id = forecast1.insert_one(data_dict)
                self.Insertion_ids.append(t_id.inserted_id())
                for l in data_dict.get('list'):   
                    Alerts(self.type, l)   # Checking for alerts in each data set and the function will save appropriate text.
            time.sleep((2.0*3600) - (time.time() - st)) # Delay of 2 hours according to the permissions of the API
            st = time.time()
                    
            
    def WeatherMap(self):
        global foremaps, API_KEYS_LIST, City_List, gfs, IMG_ID
        List_ = ['clouds_new', 'precipitation_new', 'pressure_new', 'wind_new', 'temp_new']
        self.Insertion_ids = []
        self.type = 'W_M'
        st = time.time()
        while True:
            print "Running thread: ", self.threadID, " named: ", self.name_
            for city in City_List:
                lon, lat = getCoord(city[0])    # Name of city = city[0]
                for mapp in List_:
                    urll = get_url(city[1], self.API_key, self.type, lon, lat, mapp)
                    try:    # Saving only the url in the Collection
                        ct = time.time()
                        map_doc = {ct:{str(city[0]):str(urll)}}   # map_doc contains: {<time-stamp> : {<city_name>:<url>}}
                        t_id = foremaps.insert_one(map_doc)
                        self.Insertion_ids.append(t_id.inserted_id())
                    except:
                        print ("Image of weather map named: %s, could not be saved for %s.") %(mapp, city[0])
            
            time.sleep((3.0*3600) - (time.time() - st)) # Three hours of sleep
            st = time.time()
    
    def DisplayMap(self):
        global foremaps
        st = time.time()
        while True:
            print "Running thread: ", self.threadID, " named: ", self.name_
            li = []
            docus = foremaps.find()
            for ress in docus:
                for key in ress:
                    li.append(float(key))
            li = sorted(li)         
            img_url = ress.get(li[-1])      # Last element in li is the latest time_stamp: also retreiving the url from mongodb
            img = mpimg.imread(img_url)
            plt.imshow(img)
            plt.show(block = False)     # The control is given back to the code even after the image is shown.
            time.sleep((5.0*60) - (time.time() - st))   # Updates the image after every 5 minutes
            st = time.time()
            plt.close()
    
        
        
def getCoord(name):
    lon = raw_input("Please enter the longitude of the city, %s", name)   
    lat = raw_input("Please enter the latitude of the city, %s", name)
    return lon, lat

def Alerts(typ, l):
    global Freezing_Temp
    date_today = datetime.date.today()
    
    for dt in Alerts_Dict:
        if dt < date_today:
            del Alerts_Dict[dt]
    
    if typ == 'D_5_3':
        tempr = CtoF(l.get('main').get('temp'))
        if tempr <= Freezing_Temp:
            Alerts_Dict[str(time_converter(l.get('dt')))] = "Warning! EXTREME COLD WARNING IN EFFECT AROUND " + str(datetime.datetime.fromtimestamp(
        int(l.get('dt'))))
        wemain = l.get('weather')[0].get('main')
        if "rain" in wemain.lower():
            Alerts_Dict[str(time_converter(l.get('dt')))] = "ALERT! THERE IS A CHANCE OF RAINFALL AROUND " + str(datetime.datetime.fromtimestamp(
        int(l.get('dt'))))
        if bool(l.get('snow')):
            Alerts_Dict[str(time_converter(l.get('dt')))] = "ALERT! THERE IS A CHANCE OF SNOWFALL AROUND " + str(datetime.datetime.fromtimestamp(
        int(l.get('dt'))))
            
        
    elif typ == 'D_16_24':
        tem_dic = l.get('temp')
        for key in tem_dic:
            if CtoF(tem_dic[key]) < Freezing_Temp:
                Alerts_Dict[str(time_converter(l.get('dt')))] = "Warning! EXTREME COLD WARNING IN EFFECT ON " + str(datetime.date.fromtimestamp(
        int(l.get('dt'))))
                break
        if "rain" in wemain.lower():
            Alerts_Dict[str(time_converter(l.get('dt')))] = "ALERT! THERE IS A CHANCE OF RAINFALL AROUND " + str(datetime.datetime.fromtimestamp(
        int(l.get('dt'))))


def time_converter(time):
    converted_time = datetime.date.fromtimestamp(
        int(time)
    )
    return converted_time

def CtoF(val):
    F = ((9.0/5)*int(val)) + 32
    return F

def get_url(cityid, raw_api, typ, lon, lat, mapp):
    part_url = 'http://api.openweathermap.org/data/2.5/forecast?id='
    extrapart = ''
    if typ == 'W_M':
        return 'http://tile.openweathermap.org/' + str(mapp) + '/5/' + str(lat) +'/' + str(lon) +'.png?appid=' + str(raw_api)
    elif typ == 'D_5_3':
        part_url = 'http://api.openweathermap.org/data/2.5/forecast?id='
        extrapart = ''
    elif typ == 'D_16_24':
        part_url = 'http://api.openweathermap.org/data/2.5/forecast/daily?id='
        extrapart = '&cnt=16'
    stds = 'metric'
    # user_api = '7b3b1086cd3f7fa3ad88f36131293ad4' 
    '''
    http://api.openweathermap.org/data/2.5/forecast?id=524901 # For 5 Days/3 hours
    http://api.openweathermap.org/data/2.5/forecast/daily?id={city ID} # For 16 days/Daily
    
    '''
    api_url = part_url + str(cityid) + extrapart + '&mode=json&units=' + stds + '&APPID=' + raw_api
    return api_url

def update_data_dict(api_url):
    url = urllib.urlopen(api_url)
    output = url.read().decode('utf-8')
    api_dict = json.loads(output) # Downloaded API data...
    url.close()
    print api_dict
    return api_dict

# Create new threads
thread1 = myThread(1, 'Config_file_reloader_thread')
thread2 = myThread(2, 'Forecaster_5days_3hours_thread')
thread3 = myThread(3, 'Forecaster_16days_daily_thread')
thread4 = myThread(4, 'Current_Weather_maps_thread')
thread5 = myThread(5, 'Latest_weather_map_displayer_thread')

# Start new Threads
thread1.cnfg_refresh()()
thread2.D_5_3()
thread3.D_16_24()
thread4.WeatherMap()
thread5.DisplayMap()


 