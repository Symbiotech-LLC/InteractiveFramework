
import argparse


def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('--module', '--mod', '-module', '-mod', '-m', '--m', action='store', dest='module', required=False,
		help='If you know module and what arguments that module accepts, you can call it directly (good for jenkins runs)')
	arguments = parser.parse_args()
	
	return arguments


def open_wiki():
	import os, webbrowser
	path = 'base' + os.sep + 'docs' + os.sep + 'InteractiveFramework' + os.sep + 'site' + os.sep + 'index.html'
	
	if os.path.exists(path):
		webbrowser.open('file://' + os.path.realpath(path))
	else:
		print("Wiki not found")
