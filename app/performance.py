#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import calendar
from httplib2 import Http
from apiclient.errors import HttpError
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build
from datetime import date, datetime, timedelta 


class ServiceStats:
  def __init__(self, name, url, sessions, converters_session, loyalty_session, start_of_month, end_of_month):
    self.name = name
    self.url = url
    self.sessions = "%s" % human_format(int(sessions))
    self.sessions_alt= "{:,}".format(int(sessions))
    self.converters_session_alt = "{:,}".format(int(converters_session))
    self.loyalty_session_alt = "{:,}".format(int(loyalty_session))
    self.start_of_month = start_of_month
    self.end_of_month = end_of_month
    try:
      self.converters_session = "{:.0%}".format((float(converters_session) /(float(sessions))))
    except Exception, e:
      self.converters_sessione = '0%'
    try:
      self.loyalty_session = "{:.0%}".format((float(loyalty_session) /(float(sessions))))
    except Exception, e:
      self.loyalty_session = '0%'

def get_previous_month_dates(when=None): 
 if not when: when = datetime.today() 
 this_first = date(when.year, when.month, 1) 
 prev_end = this_first - timedelta(days=1) 
 prev_first = date(prev_end.year, prev_end.month, 1) 
 return prev_first, prev_end 

start_of_month = str(get_previous_month_dates()[0])
end_of_month = str(get_previous_month_dates()[1])
    
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
        
    if magnitude < 2:
        return '%.0f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
 

def get_service():
  client_email = '109932394679-rb01o095vuqbk7dm3rl3fjnsvu41olhv@developer.gserviceaccount.com'
  with open("secure_key.p12") as f:
    private_key = f.read()

  credentials = SignedJwtAssertionCredentials(client_email, private_key,
    'https://www.googleapis.com/auth/analytics.readonly')

  http = Http()
  credentials.authorize(http)

  service = build('analytics', 'v3', http=http)
  return service

def get_profiles(service):
  
  try:
    #Get all the profiles the users is allocated to   
    profiles = service.management().profiles().list(
            accountId='~all',
            webPropertyId='~all').execute().get('items')
  
    return profiles 
  except TypeError, error:
    # Handle errors in constructing a query.
    print ('There was an error in constructing your query : %s' % error)
  except HttpError, error:
    # Handle API errors.
    print ('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason()))
  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')
  
def get_sessions(service, profile_id):

  # Use the Analytics Service Object to query the Core Reporting API
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_of_month,
      end_date=end_of_month,
      metrics='ga:sessions').execute()

def get_conversion_data(service, profile_id):

  # Use the Analytics Service Object to query the Core Reporting API
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_of_month,
      end_date=end_of_month,
      metrics='ga:sessions',
      segment='gaid::-9').execute()

def get_loyalty_data(service, profile_id):

  # Use the Analytics Service Object to query the Core Reporting API
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_of_month,
      end_date=end_of_month,
      dimensions='ga:daysSinceLastSession',
      filters='ga:daysSinceLastSession=~^[0-9]$;ga:userType=@returning visitor',
      metrics='ga:sessions').execute()


#users::condition::ga:daysSinceLastSession<10;sessions::condition::ga:userType=@returning visitor

def get_dashboard_stats():
  results = []

  service = get_service()
  profiles = get_profiles(service)

  for profile in profiles:
    # print(profile)
    service_results = get_sessions(service, profile.get('id'))

    profileName = service_results.get('profileInfo').get('profileName')
    profileUrl = profile.get('websiteUrl')

    if 'rows' in service_results:
      profileSessions = service_results.get('rows')[0][0]
    else:
      profileSessions = 0
    
    profileConvertorsData = get_conversion_data(service, profile.get('id'))
    
    if 'rows' in profileConvertorsData:
      profileConvertors = profileConvertorsData.get('rows')[0][0]
    else:
      profileConvertors = 0

    profileLoyaltyData = get_loyalty_data(service, profile.get('id'))

    if 'rows' in profileLoyaltyData:
      rows = profileLoyaltyData.get('rows')
      profileLoyalty = sum([int(r[1]) for r in rows])
    else:
      profileLoyalty = 0

    results.append(ServiceStats(profileName, profileUrl, profileSessions, profileConvertors, profileLoyalty, start_of_month, end_of_month))

  return results

def main(argv):
    service = get_service()
    # Note: This code assumes you have an authorized Analytics service object.
    # See the Segments Developer Guide for details.

    # Example #1:
    # Requests a list of segments to which the user has access.
    try:
      segments = service.management().segments().list().execute()

    except TypeError, error:
      # Handle errors in constructing a query.
      print 'There was an error in constructing your query : %s' % error

    except HttpError, error:
      # Handle API errors.
      print ('There was an API error : %s : %s' %
             (error.resp.status, error.resp.reason))

    # Example #2:
    # The results of the list method are stored in the segments object.
    # The following code shows how to iterate through them.
    for segment in segments.get('items', []):
      print 'Segment Id         = %s' % segment.get('id')
      print 'Segment kind       = %s' % segment.get('kind')
      print 'Segment segmentId  = %s' % segment.get('segmentId')
      print 'Segment Name       = %s' % segment.get('name')
      print 'Segment Definition = %s' % segment.get('definition')
      if segment.get('created'):
        print 'Created    = %s' % segment.get('created')
        print 'Updated    = %s' % segment.get('updated')
      print
    
if __name__ == '__main__':
  main(sys.argv)