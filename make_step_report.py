import os
import csv
from jinja2 import Environment, FileSystemLoader

from tabulate.tabulate import tabulate

import download_stats
import step_visitors

this_dir = os.path.dirname( os.path.realpath( __file__ ) )
sphinx_dir = os.path.join(this_dir, "sphinx")
output_dir = os.path.join(this_dir, "output")

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

if __name__ == "__main__":
  main()
