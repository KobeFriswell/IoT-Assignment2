# References for research:
#    1: https://developers.google.com/calendar/quickstart/python
#    2: https://developers.google.com/calendar/overview

from __future__ import print_function
import datetime
from datetime import timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = "https://www.googleapis.com/auth/calendar"
#connect to given account (admin account to store booking dates)
try:    #alternate credential file check depending on location
    store = file.Storage("token.json")
    creds = store.get()
    if(not creds or creds.invalid):
        flow = client.flow_from_clientsecrets("credentials.json", SCOPES)

        creds = tools.run_flow(flow, store)
except:
    store = file.Storage("MasterPi/token.json")
    creds = store.get()
    if(not creds or creds.invalid):
        flow = client.flow_from_clientsecrets("MasterPi/credentials.json", SCOPES)
        
service = build("calendar", "v3", http=creds.authorize(Http()))

class CalendarUtils:
    """
        class CalendarUtils for all calendar methods used to connect with google calendar.
    """
    def createEvent(self, user, userEmail, rego, startDate, endDate):
        """
            takes variables user,userEmail, rego and dates to create a new event on
            companies google calendar, using credentials stored in MasterPi folder
        """
        time_start = "{}T00:00:00+10:00".format(startDate)
        time_end = "{}T23:59:00+10:00".format(endDate)
        #even data to be stored when event is created
        event = {
            "summary": "Car Booking",
            "location": "RMIT Building 14",
            "start": {
                "dateTime": time_start,
                "timeZone": "Australia/Melbourne",
            },
            "end": {
                "dateTime": time_end,
                "timeZone": "Australia/Melbourne",
            },
            "attendees": userEmail,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    { "method": "email", "minutes": 5 },
                    { "method": "popup", "minutes": 10 },
                ],
            }
        }
        #add event to calendar
        event = service.events().insert(calendarId = "ofnldnuuj1dbhn36tlnas84nv0@group.calendar.google.com", body = event).execute()
        event = service.events().get(calendarId='ofnldnuuj1dbhn36tlnas84nv0@group.calendar.google.com', eventId=event['id']).execute()
        event['description'] = 'Booking for ' + rego + '\nBooking ID: ' + event['id']
        service.events().update(calendarId='ofnldnuuj1dbhn36tlnas84nv0@group.calendar.google.com', eventId=event['id'], body=event).execute()
        print("Booking created: {}".format(event.get("htmlLink")))
        return event['id']  #return id so that event can be accessed by user

    def getCalendarID(self):
        """
            gets calendar ID link to output to user to allow them to access that given booking on their calendar
        """
        page_token = None
        while True:
            #get the id for the current calendar
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

    def deleteEvent(self, event):
        """
            removes given event from companies google calendar
        """
        service.events().delete(calendarId='ofnldnuuj1dbhn36tlnas84nv0@group.calendar.google.com', eventId=event).execute()

