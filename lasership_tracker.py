#!/usr/bin/env python3

# for getting and parsing the LS JSON API
import requests

# time handling
import datetime
import time

# Import the email modules we'll need
import smtplib
from email.message import EmailMessage

# utility libraries
from collections import defaultdict

def get_args():
    import argparse

    parser = argparse.ArgumentParser(description='Monitor a Lasership package via the JSON API.')
    parser.add_argument("LSID", help="Lasership tracking number (e.g. '1LS1234567890000-1')",
                        type=str)
    parser.add_argument("email", help="email address to notify",
                        type=str)

    parser.add_argument("--pollfreq", help="polling interval (in seconds); default: 60",
                        default=60,
                        type=int)
    parser.add_argument("--console", help="log records to console",
                        action="store_true")
    parser.add_argument("--no-email", help="disable emailing",
                        action="store_true")
    parser.add_argument("--boxname", help="Nickname for box; defaults to nothing", type=str,
                        default='')
    args = parser.parse_args()
    
    #if args.boxname is None: args.boxname = args.LSID
    
    # print(args)
    
    return args.LSID, args.email, args.boxname, args.pollfreq, args.console, args.no_email

def send_email(msg):
    '''sends the EmailMessage via smtplib'''
    try:
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
        pass
    except:
        print('Error: Email msg failed!')
        return False
    return True

def make_email(event, address, boxname):
    # TODO: make configurable parameters!
    '''given JSON dict, returns EmailMessage of msg'''
    msg = EmailMessage()

    msg['Subject'] = f"LS {boxname}: {event['EventLabel']}" # latest 'thing' (e.g. 'Out for Delivery')
    msg['From'] = address
    msg['To'] = address
    
    msgbody = parse_LS_event(event)
    
    msg.set_content(msgbody)
    
    return msg

def get_latest_time(event):
    '''given a JSON dict, returns a datetime object from the timestamp'''
    try:
        time = event['DateTime']
        time = datetime.datetime.strptime(event['DateTime'], '%Y-%m-%dT%H:%M:%S')
    except KeyError:
        print('warning: no timestamp!')
        time = datetime.datetime.fromordinal(2)
    except:
        print('Error! timestamp problems!')
        time = datetime.datetime.fromordinal(2)
        
    return time

def poll_LS_status(LSID):
    '''polls LS status; returns latest event, or empty dict if failed'''
    try:
        data = requests.get(f'https://www.lasership.com/track/{LSID}/json')
        print(data)
        print(data.json())
        if data.status_code != 200:
            print('Warning! Abnormal API response:', data.status_code)
            #raise ValueError
        if 'Error' in data.json():
            if data.json()['Error']: print('Warning! LS API Error!')
        else:
            data = data.json()['Events'][0]
    except:
        data = {}
    
    data['DetectedTime'] = datetime.datetime.now()
    data['LSID'] = LSID
    data = defaultdict(str, data)
        # in case of missing fields, we get empty strings instead of KeyErrors
    return data
    
def parse_LS_event(event):
    '''accepts an event as a JSON dict, and returns a nicely-formatted text block'''
    content = ''
    
    status = event['EventLabel'] # latest 'thing' (e.g. 'Out for Delivery')
    time = get_latest_time(event).strftime('%I:%M %p on %a, %B %d')
    location = f"{event['City']}, {event['State']}"
    detect_time = event['DetectedTime'].strftime('%I:%M %p')
    
    content += f'The package became "{status}" at {time} in {location}. \n\n'
    
    LSID = event['LSID']
    content += f'LSID: {LSID}\n\n'

    if status == 'Delivered':
        location = event["Location"]
        content += f'The package was delivered to "{location}".\n\n'
    
    content += f'This was detected at {detect_time}.\n\n'
    
    content += str(event)
    #if laststatus != 'Out for Delivery': break
    #print('still waiting...')
    #print(datetime.datetime.now().isoformat())
    #time.sleep(60)
    
    return content

def lasership_tracker(LSID, email, boxname, pollfreq=60, console=False, no_email=False):
    
    delivered = False
    prev_time = datetime.datetime.fromordinal(2) 
        # previous event time; initialized sometime in the distant past
    
    print('Now monitoring...')
  
    while not delivered:
        event = poll_LS_status(LSID)
        
        last_time = get_latest_time(event)
        
        if last_time > prev_time:
            # if there is a new update

            msg = make_email(event, email, boxname)
            if not no_email: send_email(msg)
            prev_time = last_time
            
            if console:
                print(parse_LS_event(event))
        
            if event['EventLabel'] == 'Delivered':
                delivered = True
        
        time.sleep(pollfreq)
    return 0

if __name__ == '__main__':
    lasership_tracker(*get_args())
