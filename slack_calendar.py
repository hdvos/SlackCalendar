from bs4 import BeautifulSoup
from datetime import datetime
import os
import random
import re
import requests
from slack import WebClient
from slack.errors import SlackApiError
import time

url = "https://www.checkiday.com/"
cwd = os.getcwd()
 
class SlackCalendar(object):
    def __init__ (self, creds_file = "creds.txt", datefile=".date.txt", post_time='8:00', frequency = 15):
        self.creds_file = creds_file
        self.read_creds()
        
        self.datefile = datefile
        
        self.post_time = post_time
        self.post_hr = int(post_time.split(':')[0])
        self.post_min = int(post_time.split(':')[1])
        
        assert frequency < 60
        self.frequency = frequency
        
        self.client = WebClient(self.creds['Token'])
        
    def check_time(self):
        now = datetime.now()
        print(f"{self.post_min} <= {now.minute}")
        
        if now.hour == self.post_hr and self.post_min <= now.minute:
            return True
        else:
            print(f"{now.hour}:{now.minute}:{now.second}")
            return False
        
    
    def check_date(self):
        today = datetime.today()
        
        datefile = os.path.join(cwd, self.datefile)
        if not os.path.exists(datefile):
            with open(self.datefile, 'wt') as out:
                out.write(today.strftime('%d-%m-%Y'))
            return True
        
        else:
            with open(self.datefile, 'rt') as f:
                content = f.read().strip()
            
            if today.strftime('%d-%m-%Y') == content:
                print("already posted sth today.")
                return False
            else:
                with open(self.datefile, 'wt') as out:
                    out.write(today.strftime('%d-%m-%Y'))
                return True
                            
        
    def read_creds(self):
        with open (self.creds_file, 'rt') as f:
            content = f.readlines()
        
        self.creds = {}
        self.creds['AppID'] = content[0].split(':')[1].strip()
        self.creds['ClientID'] = content[1].split(':')[1].strip()
        self.creds['Client Secret'] = content[2].split(':')[1].strip()
        self.creds['Signing Secret'] = content[3].split(':')[1].strip()
        self.creds['Token'] = content[5].split(':')[1].strip()
        print(f'-{self.creds["Token"]}-')
        
    
    def download_page(self):
        resp = requests.get(url)
        html = resp.text
        return html
    
    def get_dayname(self, candidate):
        candidate_sentence = candidate.text
        candidate_sentence = cs = candidate_sentence.split()
        i = 2
        dayname_words = []
        while not( cs[i].lower() == 'which' and cs[i+1].lower() == 'is' and cs[i+2].lower() == 'observed'):
            word = cs[i]
            # print(word)
            dayname_words.append(word)
            i += 1
            if i == 100:
                print("ERROR! i == 100" )
                break
        dayname = ' '.join(dayname_words)
    
        return dayname
    
    def get_url(self, candidate):
        url = candidate.select_one('a')['href']
        return url
    
    def get_today(self):
        today = datetime.today()
        today = today.strftime('%B-%d')
        return today
    
    def compose_message(self, date, dayname, url):
        msg = """
[{}]: Happy {}!!!

For more info, check {}
""".format(date, dayname, url)

        #msg = ' x' 
        return msg
    
    def post_message(self, msg):
        try:
            response = self.client.chat_postMessage(
                channel='#oh_happy_day',
                text=msg)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

    def process_page(self):
        html = self.download_page()
        soup = BeautifulSoup(html, features = 'lxml')
        candidates = soup.select('.holiday')
        
        succeeded = False
        while not succeeded:
            try:
                selected_candidate = random.choice(candidates)
                dayname = self.get_dayname(selected_candidate)
                succeeded = True
            except Exception as e:
                print(e)
                time.sleep(5)
                print("Try again")
                continue
                
        url = self.get_url(selected_candidate)
        
        date = self.get_today()
        msg = self.compose_message(date, dayname, url)
        print(msg)
        self.post_message(msg)
        
    def run(self):
        while True:
            if self.check_time():
                if self.check_date():
                    self.process_page()
            
            print(f"Sleep for {self.frequency} minutes")
            print("-----------------------------------")
            time.sleep(self.frequency * 60)
            
sc = SlackCalendar(post_time='08:30', frequency = 20)
sc.run()
