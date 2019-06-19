#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author:
Nick Serra <nick.serra@perficient.com>

Summary:
		Fix mkdocs site after it has been built.
		When storing / organizing .md files in multiple folder, mkdocs does not add index.html to the end of the hrefs
"""

import os, sys, argparse, glob
import mkdocs
from bs4 import BeautifulSoup


def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-path', '-p', action='store', dest='site_path', required=True, help='Enter path to mkdocs site directory')
	arguments = parser.parse_args()
	
	if not os.path.exists(arguments.site_path):
		parser.error(arguments.site_path + " Does NOT Exist..... Exiting")
	
	return arguments


class fix_mkdocs:
	def __init__(self, arguments):
		self.arguments = arguments
		self.target_files = list()
	
	def main(self):
		for root, subFolders, files in os.walk(self.arguments.site_path):
			# for directory in subFolders:
			# 	print(os.path.join(root, directory))
			
			for filename in files:
				if filename == 'index.html':
					print(os.path.join(root, filename))
					self.target_files.append(os.path.join(root, filename))
		print(" ")
		for file in self.target_files:
			self.fix_links(file)
	
	def fix_links(self, file):
		print("Checking ", file)
		with open(file, 'r') as f:
			filedata = f.readlines()
		
		for index, line in enumerate(filedata):
			soup = BeautifulSoup(line, 'html.parser')
			for a in soup.find_all('a', href=True):
				if str(a['href']).endswith('/'):
					print(a['href'] + ' ---> ' + a['href'] + 'index.html')
					newline = line.replace(a['href'], a['href'] + 'index.html')
					filedata[index] = newline
				elif str(a['href']).endswith('..'):
					print(a['href'] + ' ---> ' + a['href'] + '/index.html')
					newline = line.replace(a['href'], a['href'] + '/index.html')
					filedata[index] = newline
		filedata = '\n'.join(filedata)
		with open(file, 'w') as outfile:
			outfile.write(filedata)
		outfile.close()
				

if __name__ == '__main__':
	args = get_arguments()
	fix_mkdocs(args).main()