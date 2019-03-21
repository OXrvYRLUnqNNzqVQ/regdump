#!/usr/bin/python
import argparse
import sh
from bs4 import BeautifulSoup
import pandas as pd
import hashlib

parser = argparse.ArgumentParser()

parser.add_argument('-k', action='store_true')
parser.add_argument('-n', action='store_true')
parser.add_argument('-d', action='store_true')
parser.add_argument('-t', action='store_true')
parser.add_argument('file')
parser.add_argument('--truncate', default=50, type=int, help='truncate output cols')
args = parser.parse_args()
infile = args.file

if args.truncate == 0:
	pd.options.display.max_colwidth = 128
else:
	pd.options.display.max_colwidth = args.truncate

xml = unicode(sh.hivexml(infile))
xml = xml.encode('utf8', 'replace')

data = []

def get_root_elements(path_to_file):
    soup = BeautifulSoup(path_to_file, 'lxml')
    all_elements = soup.find_all('value')
    return all_elements

def get_path(element):
	path = []
	for parent in element.parents:
		if parent.name == "node":
			if parent['name'] is not "None":
				path.append(parent['name'])
	return '/'.join(path[::-1][1:])

for i in get_root_elements(xml):
	row = []
	name_ = i.get('key') if i.get('key') is not None else "(Default)"
	type_ = i.get('type') if i.get('type') is not None else "(value not set)"
	data_ = i.get('value') if i.get('type') is not None else "(value not set)"
	if str(type_)=="binary": data_ = hashlib.sha224(str(data_)).hexdigest()
	if args.k: row.append((get_path(i))) 
	if args.n: row.append((name_)) 
	if args.t: row.append((type_)) 
	if args.d: row.append((data_)) 
	data.append(row)

df = pd.DataFrame(data)
print(df.to_string(index=False, header=False))
