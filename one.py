'''
Created on Jul 21, 2017

@author: rjw0028
'''
import datetime
import json
import urllib
import threading
import time

thread_num = 0

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID):
        global thread_num
        thread_num += 1
        self.threadID = threadID
            
    def D_5_3(self, cityid, API_key):
        self.cityid = cityid
        self.API_key = API_key
        
    def D_16_24(self, cityid, API_key):
        self.cityid = cityid
        self.API_key = API_key
        
    def WeatherMaps(self, cityid, API_key):
        self.cityid = cityid
        self.API_key = API_key
        
    def Map2Window(self):
    
    def Alerts(self):
        
        
        

def get_time(time):
    t = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%k:%M ')
    return t

def get_city_id():
    cityid = int(raw_input('Please enter the city ID for the desired city according to city.list.json.gz found at http://bulk.openweathermap.org/sample/'))
    return cityid

def get_api_key():
    API_access_key = raw_input('Please enter the API key from https://home.openweathermap.org/api_keys')
    return API_access_key

def get_url():
    stds = 'metric'
    cityid = get_city_id()
    raw_api = get_api_key()
    # user_api = '7b3b1086cd3f7fa3ad88f36131293ad4' 
    part_url = 'http://api.openweathermap.org/data/2.5/weather?id=' # Only for Current Weather 
    '''
    http://api.openweathermap.org/data/2.5/forecast?id=524901 # For 5 Days/3 hours
    http://api.openweathermap.org/data/2.5/forecast/daily?id={city ID} # For 16 days/Daily
    
    '''
    api_url = part_url + str(cityid) + '&mode=json&units=' + stds + '&APPID=' + raw_api
    return api_url

def update_data_dict(api_url):
    url = urllib.urlopen(api_url)
    output = url.read().decode('utf-8')
    api_dict = json.loads(output)
    url.close()
    print api_dict
    return api_dict





if __name__ == '__main__':
    try:
        url = get_url()
        updated_data = update_data_dict(url)
        
    except IOError:
        print('no internet')