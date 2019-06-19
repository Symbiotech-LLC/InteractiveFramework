#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
sys.path.append(".")
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
import os, sys, time, platform, argparse, getpass
import sqlite3
import pandas as pd


# Global Variables
date = time.strftime("%m-%d-%y")  # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%I_%M")  # Time
time_of_execution = str(time.strftime("%I_%M_%p"))  # Time
current_dir = os.path.dirname(os.path.realpath(__file__))  # Get Current Directory of Running Script
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # Get Parent of Current Directory of Script
parent_of_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))  # Get Parent of Current Directory of Script

sql_completer = WordCompleter([
	'abort', 'action', 'add', 'after', 'all', 'alter', 'analyze', 'and',
	'as', 'asc', 'attach', 'autoincrement', 'before', 'begin', 'between',
	'by', 'cascade', 'case', 'cast', 'check', 'collate', 'column',
	'commit', 'conflict', 'constraint', 'create', 'cross', 'current_date',
	'current_time', 'current_timestamp', 'database', 'default',
	'deferrable', 'deferred', 'delete', 'desc', 'detach', 'distinct',
	'drop', 'each', 'else', 'end', 'escape', 'except', 'exclusive',
	'exists', 'explain', 'fail', 'for', 'foreign', 'from', 'full', 'glob',
	'group', 'having', 'if', 'ignore', 'immediate', 'in', 'index',
	'indexed', 'initially', 'inner', 'insert', 'instead', 'intersect',
	'into', 'is', 'isnull', 'join', 'key', 'left', 'like', 'limit',
	'match', 'natural', 'no', 'not', 'notnull', 'null', 'of', 'offset',
	'on', 'or', 'order', 'outer', 'plan', 'pragma', 'primary', 'query',
	'raise', 'recursive', 'references', 'regexp', 'reindex', 'release',
	'rename', 'replace', 'restrict', 'right', 'rollback', 'row',
	'savepoint', 'select', 'set', 'table', 'temp', 'temporary', 'then',
	'to', 'transaction', 'trigger', 'union', 'unique', 'update', 'using',
	'vacuum', 'values', 'view', 'virtual', 'when', 'where', 'with',
	'without'], ignore_case=True)


def sql_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('--database', '--db', '-database', '-db', action='store', dest='database', required=False, help='Enter path to sqlite database')
	parser.add_argument('--query', '--q', '-query', '-q', action='store', dest='query', required=False, help='Enter SQLite query')
	arguments = parser.parse_args()
	
	if not arguments.database:
		arguments.database = input('What is the path to your sqlite database?:\n')
	
	if os.path.exists(arguments.database):
		arguments.database = str(arguments.database)
	elif os.path.exists(parent_of_parent_dir + os.sep + 'database' + os.sep + arguments.database):
		arguments.database = parent_of_parent_dir + os.sep + 'database' + os.sep + str(arguments.database)
	else:
		print(arguments.database + " does NOT exist")
		exit()
		
	return arguments


class QueryDB:
	def __init__(self, arguments):
		self.arguments = arguments
		self.string_query = None
		self.last_query = None
		self.headers = None
		self.results = None
		self.last_result = None
		self.available_tables = self.show_tables()
	
	def main(self):
		if self.arguments.query:
			try:
				self.string_query, self.headers, self.results = self.query(self.arguments.query)
				if self.string_query and self.headers and self.results:
					self.last_query = self.string_query
					self.last_result = pd.DataFrame(self.results, columns=self.headers)
				print(self.query)
				print(" ")
				print(self.last_result)
			except Exception as e:
				print(e)
				pass
		else:
			self.query_prompt()
		return self.string_query, self.headers, self.results
	
	def query_prompt(self):
		print("\nPath to Database: " + str(self.arguments.database))
		print(" ")
		
		# self.help()
		# session = PromptSession()
		# session = PromptSession(lexer=PygmentsLexer(SqlLexer))
		session = PromptSession(lexer=PygmentsLexer(SqlLexer), completer=sql_completer)
		while True:
			try:
				print("Available Tables:")
				for table in self.available_tables:
					print(table)
				print(" ")
				prompt_input = session.prompt('\nQuery > ')
				# prompt_input = session.prompt('\nQuery > ', completer=self.command_completer)
			except KeyboardInterrupt:
				continue
			except EOFError:
				break
			else:
				if prompt_input == "quit" or prompt_input == 'exit':
					break
				else:
					try:
						self.string_query, self.headers, self.results = self.query(prompt_input)
						if self.string_query and self.headers and self.results:
							self.last_query = self.string_query
							self.last_result = pd.DataFrame(self.results, columns=self.headers)
						print(self.query)
						print(" ")
						print(self.last_result)
					except Exception as e:
						print(e)
						pass
					
	def query(self, query):
		print("\nQuerying " + str(self.arguments.database))
		print("Query: ", query)
		print(" ")
		db = sqlite3.connect(self.arguments.database)
		cursor = db.cursor()
		cursor.execute(query)
		title = [i[0] for i in cursor.description]
		# print(title)
		all_results = cursor.fetchall()
		results = pd.DataFrame(all_results, columns=title)

		return query, title, all_results
	
	def show_tables(self):
		available_tables = list()
		db = sqlite3.connect(self.arguments.database)
		cursor = db.cursor()
		cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;')
		results = cursor.fetchall()
		for item in results:
			available_tables.append(item[0])
		return available_tables


if __name__ == '__main__':
	args = sql_arguments()
	SQL = QueryDB(args)
	SQL.main()
