#!/usr/bin/env python

import sys
import os
import requests
import time
import json
import datetime
import numpy as np

this_dir = os.path.dirname( os.path.realpath( __file__ ) )
output_dir = os.path.join(this_dir, "output")
if not os.path.exists(output_dir):
  os.makedirs(output_dir)
gnuplot_dir = os.path.join(this_dir, "gnuplot")

localconfig = os.path.join(os.path.dirname(__file__), 'config.local')
if not os.path.exists(localconfig):
  raise RuntimeError("You need to set up a config.local file")
with open(localconfig) as localconfig_stream:
  config = json.load(localconfig_stream)

def get_unique_visitors_for_range(start, end):
  url = "http://step.esa.int/piwik/index.php?"

  # http://developer.piwik.org/api-reference/reporting-api
  params = {}
  params["idSite"] = "6"
  params["period"] = "week"
  params["date"] = "{start}".format(start=start.isoformat())
  params["format"] = "json"
  params["token_auth"] = config['piwik_auth_token']
  params["module"] = "API"
  params["method"] = "VisitsSummary.getUniqueVisitors"
  params["expanded"] = "1"
  params["flat"] = "1"
  r = requests.get(url, params=params)
  jsonresult = r.json()
  return jsonresult[0]["nb_uniq_visitors"]
  
def previous_monday(day):
  # weekday == 0 => it's Monday
  return day - datetime.timedelta(days=day.weekday())

def monday_iter(start, end):
  starting_monday = previous_monday(start)
  ending_monday = previous_monday(end)
  while starting_monday < ending_monday:
    yield starting_monday
    starting_monday += datetime.timedelta(days=7)

def generate():
  origin = datetime.date(2015, 6, 15)
  today = datetime.date.today()
  with open(os.path.join(output_dir, 'unique_visitors.dat'), 'w') as visitors_file :
    for start in monday_iter(origin, today):
      end = start + datetime.timedelta(days=6)
      unique_visitors =  get_unique_visitors_for_range(start, end)
      line=start.isoformat() + ' to ' + end.isoformat() + ';' + str(unique_visitors) + '\n'
      visitors_file.write(line)
  os.system("gnuplot %s" % (os.path.join(gnuplot_dir, 'unique_visitors.gnuplot')))

if __name__ == "__main__":
  generate()
  
  
  
  
