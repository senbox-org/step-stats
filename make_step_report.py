import os
import csv
from jinja2 import Environment, FileSystemLoader
import json

from tabulate.tabulate import tabulate

import download_stats
import step_visitors
import sendmail

this_dir = os.path.dirname( os.path.realpath( __file__ ) )
sphinx_dir = os.path.join(this_dir, "sphinx")
output_dir = os.path.join(this_dir, "output")

localconfig = os.path.join(os.path.dirname(__file__), 'config.local')
if not os.path.exists(localconfig):
  raise RuntimeError("You need to set up a config.local file")
with open(localconfig) as localconfig_stream:
  config = json.load(localconfig_stream)

def read_csv(filename) :
   with open(filename, 'rb') as datafile:
     reader = csv.reader(datafile, delimiter=';')
     data = [row for row in reader]
   return data

def csv_to_string(filename):
  return tabulate(read_csv(filename), headers="firstrow", tablefmt="rst")

def update_rst(context):
  env = Environment(loader=FileSystemLoader(sphinx_dir))
  template = env.get_template('index.rst.j2')
  with open( os.path.join(sphinx_dir, 'index.rst'), 'w') as outputfile:
    outputfile.write(template.render(context))

def main():
   download_stats.generate()
   step_visitors.generate()
   
   jinjacontext = {}
   jinjacontext['unique_downloads_table'] = csv_to_string(os.path.join(output_dir, 'unique_downloads.dat'))
   jinjacontext['unique_downloads_img'] = os.path.join('../output', 'unique_downloads.eps')
   jinjacontext['cumulated_unique_downloads_table'] = csv_to_string(os.path.join(output_dir, 'cumulated_unique_downloads.dat'))
   jinjacontext['cumulated_unique_downloads_img'] = os.path.join('../output', 'cumulated_unique_downloads.eps')
   jinjacontext['unique_visitors'] = csv_to_string(os.path.join(output_dir, 'unique_visitors.dat'))
   jinjacontext['unique_visitors_img'] = os.path.join('../output', 'unique_visitors.eps')
   jinjacontext['os_piechart'] = os.path.join('../output', 'os_piechart.eps')
   update_rst(jinjacontext)
   
   os.system('cd %s; make latexpdf' % sphinx_dir)

   
   sender = config['mail_from']
   to = [ config['mail_to'] ]
   subject = 'STEP Surveillance report'
   text = '''
Hello there,

Here comes the new statistics from STEP.

Your faithful employee,
     the STEP Big Brother
'''
   files = [ os.path.join(sphinx_dir, "_build/latex", "STEPSurveillanceReport.pdf"), \
             os.path.join('output', 'unique_downloads.eps'), \
             os.path.join('output', 'cumulated_unique_downloads.eps'), \
             os.path.join('output', 'unique_visitors.eps'), \
             os.path.join('output', 'os_piechart.eps') ]

   sendmail.sendmail('contact@step-email.net', to, subject, text, files) 

if __name__ == "__main__":
  main()
