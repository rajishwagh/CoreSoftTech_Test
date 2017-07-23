'''
Created on Jul 21, 2017

@author: rjw0028
'''
import datetime, time
import json
import urllib
import threading
import time
from pymongo import Connection

global timmer, confg

API_KEYS_LIST = ['626065bef7e7c8883ff84245fafffa86', '9b19df8174a6d64f5e11b01ecd7d7040', '677d1ff040e3b35576cd904925955d40']
timmer = time.time()
conIn = Connection()    # Instance of a connection. This assumes that an instance of mongod is active on Windows cmd prompt.
pymondb = conIn.weather_data    # database name is weather_data... and variable handling it is pymondb
forecast1 = pymondb.fore5d3h    # collection name is fore5d3h... and variable handling it is forecast1
forecast2 = pymondb.fore16dd    # collection name is fore16dd... and variable handling it is forecast2
foremaps = pymondb.maps         # collection name if maps... and variable handling it is foremaps





thread_num = 0
exitFlag = 0



class myThread (threading.Thread):
    def __init__(self, threadID, name_):
        global thread_num
        thread_num += 1
        self.threadID = threadID
        self.name_ = name_
            
    def D_5_3(self, cityid, API_key):
        global forecast1        # Collection as a global variable. Defined at the top
        self.type = 'D_5_3'     # type defined to use the same functions of get_url and Alerts
        self.cityid = cityid    # cityid: an integer like 2343421
        self.API_key = API_key  # API key, can be entered or obtained from the pool defined at top.
        self.url = get_url(self.cityid, self.API_key, self.type)    #getting the right URL made from the function
        self.data_dict = update_data_dict(self.url)     #downloading data using urllib in this function 
        self.all_ids = [None]*len(self.data_dict.get('list'))
        for l,n in enumerate(self.data_dict.get('list')):   
            self.all_ids[n] = forecast1.insert_one(l).inserted_id   # Saving data to the Collection as individual Documents
            self.Alerts(type)   # Checking for alerts in each data set and the function will save appropriate text.
        
    def D_16_24(self, cityid, API_key):
        global forecast2        # Collection as a global variable. Defined at the top
        self.type = 'D_16_24'
        self.cityid = cityid
        self.API_key = API_key
        self.url = get_url(self.cityid, self.API_key, self.type)
        self.data_dict = update_data_dict(self.url)
        self.all_ids = [None]*len(self.data_dict.get('list'))
        for l,n in enumerate(self.data_dict.get('list')):
            self.all_ids[n] = forecast2.insert_one(l).inserted_id
            self.Alerts(type)
        
    def WeatherMaps(self, cityid, API_key): # Still trying to figure out how to download the maps as directed.
        global foremaps         # Collection as a global variable. Defined at the top
        self.cityid = cityid
        self.API_key = API_key
        self.type = 'WeatherMaps'
        self.url = get_url(self.cityid, self.API_key, self.type)
        
        self.Map2Window(self.url)
        
    def Map2Window(self):
        x = 2
        
    def Alerts(self, type):
        x = 3
        
        
def config_file_refresh():
    global timmer, confg
    t = time.time()
    
    if t - timmer == 15:
        confg.read("C:\\Python27\locations.ini")
    
    
    
def get_time(time):
    t = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%k:%M ')
    return t

def get_city_id():
    cityid = int(raw_input('Please enter the city ID for the desired city according to city.list.json.gz found at http://bulk.openweathermap.org/sample/'))
    return cityid

def get_api_key():
    global API_KEYS_LIST
    if API_KEYS_LIST:
        API_access_key = API_KEYS_LIST[0]
    else:
        API_access_key = raw_input('Please request enter a new API key from https://home.openweathermap.org/api_keys')
    return API_access_key

def get_url(cityid, raw_api, type):
    part_url = 'http://api.openweathermap.org/data/2.5/forecast?id='
    extrapart = ''
    if type == 'D_5_3':
        part_url = 'http://api.openweathermap.org/data/2.5/forecast?id='
        extrapart = ''
    elif type == 'D_16_24':
        part_url = 'http://api.openweathermap.org/data/2.5/forecast/daily?id='
        extrapart = '&cnt=16'
    stds = 'metric'
    cityid = get_city_id()
    raw_api = get_api_key()
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





if __name__ == '__main__':
    thread1 = myThread(1, "5Days-3hrs-thread")
    thread2 = myThread(2, "16days-daily-thread")
    
    thread1.D_5_3(get_city_id(), get_api_key())
    
    try:
        
        
    except IOError:
        print('no internet')
