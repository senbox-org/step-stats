#!/usr/bin/env python

import sys
import os
import requests
import time
import json
import datetime
import numpy as np

import matplotlib as mpl
mpl.rcParams['backend']  = 'ps'
import matplotlib.pyplot as plt

# http://step.esa.int/piwik/index.php?module=CoreHome&action=index&date=2015-10-02&period=week&idSite=6#/module=Actions&action=menuGetDownloads&date=2015-10-02&period=week&idSite=6

this_dir = os.path.dirname( os.path.realpath( __file__ ) )
output_dir = os.path.join(this_dir, "output")
if not os.path.exists(output_dir):
  os.makedirs(output_dir)
gnuplot_dir = os.path.join(this_dir, "gnuplot")

platforms = [("windows", "Windows 32 bits"), ("windows-x64", "Windows 64 bits"), ("unix", "Linux"), ("macos", "Mac OSX")]

localconfig = os.path.join(os.path.dirname(__file__), 'config.local')
if not os.path.exists(localconfig):
  raise RuntimeError("You need to set up a config.local file")
with open(localconfig) as localconfig_stream:
  config = json.load(localconfig_stream)

def get_downloads_for_range(start, end):
  url = "http://step.esa.int/piwik/index.php?"

  # http://developer.piwik.org/api-reference/reporting-api
  params = {}
  params["idSite"] = "6"
  params["period"] = "range"
  params["date"] = "{start},{end}".format(start=start.isoformat(), end=end.isoformat())
  params["format"] = "json"
  params["token_auth"] = config['piwik_auth_token']
  params["module"] = "API"
  params["method"] = "Actions.getDownloads"
  params["expanded"] = "1"
  params["flat"] = "1"
  params["filter_column"] = "url"

  result = []
  for platform in platforms:
    plaform_key=platform[0]
    download_regex = "esa-snap_{platform}_2_0".format(platform=plaform_key)
    params["filter_pattern"] = download_regex
    r = requests.get(url, params=params)
    jsonresult = r.json()

    #print json.dumps(jsonresult, indent=4)
    #download_count = jsonresult[0]["nb_hits"]
    if len(jsonresult) > 0:
        unique_download_count = jsonresult[0]["nb_visits"]
    else:
        unique_download_count = 0
    result.append(unique_download_count)
  return result 

def previous_monday(day):
  # weekday == 0 => it's Monday
  return day - datetime.timedelta(days=day.weekday())

def monday_iter(start, end):
  starting_monday = previous_monday(start)
  ending_monday = previous_monday(end)
  while starting_monday < ending_monday:
    yield starting_monday
    starting_monday += datetime.timedelta(days=7)
    
def make_pie_chart(downloads_count):
  labels = [ platform[1] for platform in platforms ]
  colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
  explode = (0.1, 0.1, 0.1, 0.1) # only "explode" the 2nd slice (i.e. 'Hogs')

  fig = plt.figure()
  plt.pie(downloads_count, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
  # Set aspect ratio to be equal so that pie is drawn as a circle.
  plt.axis('equal')
  fig.savefig(os.path.join(output_dir, 'os_piechart.eps'))
    
def generate():
  origin = datetime.date(2015, 6, 15)
  today = datetime.date.today()
  
  nb_weeks = (previous_monday(today)-previous_monday(origin)).days/7
  results = np.zeros( (nb_weeks, len(platforms)), dtype=np.int )
  current_week=0
  
  with open( os.path.join(output_dir, 'unique_downloads.dat'), 'w') as downloads_file :
    with open(os.path.join(output_dir, 'cumulated_unique_downloads.dat'), 'w') as cumulated_downloads_file :
      downloads_file.write('OS;' + ';'.join(platform[1] for platform in platforms) + '\n')
      cumulated_downloads_file.write('OS;' + ';'.join(platform[1] for platform in platforms) + '\n')
      cumulated_downloads = len(platforms) * [0]
      for start in monday_iter(origin, today):
        end = start + datetime.timedelta(days=6)
        print "Getting download stat for week : {start} -> {end}".format(start=start, end=end)
        downloads = get_downloads_for_range(start, end)
        line=start.isoformat() + ' to ' + end.isoformat() + ';' + ";".join([str(value) for value in downloads]) + '\n'
        downloads_file.write(line)
        
        cumulated_downloads = [ cumulated_downloads[i] + downloads[i] for i in range(len(platforms)) ]
        line=start.isoformat() + ' to ' + end.isoformat() + ';' + ";".join([str(value) for value in cumulated_downloads]) + '\n'
        cumulated_downloads_file.write(line)
      
      # the last state of cumulated_downloads gives us the total downloads up to now.
      # prepare a pie chart for this, by OS
      make_pie_chart(cumulated_downloads)
      
  
  os.system("gnuplot %s" % (os.path.join(gnuplot_dir, 'unique_downloads.gnuplot')))
  os.system("gnuplot %s" % (os.path.join(gnuplot_dir, 'cumulated_unique_downloads.gnuplot')))
  
if __name__ == "__main__":
  generate_download_stats()
  
  
  
  
