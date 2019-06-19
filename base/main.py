#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author:
	grimmvenom <grimmvenom@gmail.com>

Resources:
https://python-prompt-toolkit.readthedocs.io/en/master/pages/tutorials/repl.html
https://bitbucket.org/LaNMaSteR53/recon-ng.git
https://github.com/thodnev/pluginlib
https://docs.python.org/3/library/importlib.html

Summary:
		Interactive Framework for various scripts
"""

from base.core.get_arguments import *
from base.core.pyCommon import *


class AEMUtility:
	def __init__(self, arguments):
		if arguments:
			self.arguments = arguments
		self.modules = list()
		self.module_dir = 'base/modules'
		self.list_modules()
		self.suggestions = ['show modules', 'show commands', 'quit', 'exit', 'help', 'wiki']
		for module in self.modules:
			self.suggestions.append('run ' + module)
			self.suggestions.append('run ' + module + ' help')

		self.command_completer = WordCompleter(self.suggestions, ignore_case=True)
		if self.arguments.module:
			# print("Module Defined:")
			# print(self.arguments.module)
			self.run_module(str(self.arguments.module))
		else:
			self.main()

	def main(self):
		self.list_commands()
		session = PromptSession()
		while True:
			try:
				prompt_input = session.prompt('\nMain > ', completer=self.command_completer)
			except KeyboardInterrupt:
				continue
			except EOFError:
				break
			else:

				if prompt_input == "show modules":
					self.show_modules()
				elif prompt_input.startswith('run '):
					self.run_module(prompt_input)
				elif prompt_input == 'help':
					self.list_commands()
					open_wiki()
				elif prompt_input == 'show commands':
					self.list_commands()
				elif prompt_input == 'wiki':
					open_wiki()
				elif prompt_input == "quit" or prompt_input == 'exit':
					break

	def list_commands(self):
		print("\nCommands\n=============================================")
		for suggestion in self.suggestions:
			print(suggestion)
		print(" ")

	def list_modules(self):
		exclude = ['core', '__pycache__']
		for dirpath, dirnames, files in os.walk(self.module_dir):
			for name in files:
				if 'core' not in dirpath:
					if name.lower().endswith('.py') and name.lower() != '__init__.py':
						filepath = os.path.join(dirpath, name)
						uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
						parent_dir = os.path.basename(uppath(filepath, 1))
						parent_of_parent_dir = os.path.basename(uppath(filepath, 2))
						if parent_dir == 'modules':
							module_name = basename(name).split('.')[0]
							self.modules.append(module_name)
						else:
							module_name = parent_dir + os.sep + basename(name).split('.')[0]
							self.modules.append(module_name)

	def show_modules(self):
		print("Modules\n=============================================")
		x = 0
		for module in self.modules:
			x += 1
			print(str(x) + ") " + str(module))

	def run_module(self, prompt_input):
		breakdown = prompt_input.split(' ')
		if prompt_input.startswith('run'):  # Run Interactive module
			module = str(breakdown[1]) + '.py'
			if len(breakdown) > 2:
				args = ' '.join(breakdown[2:])
			else:
				args = ''
		else:  # Run with Specified Module
			module = str(breakdown[0]) + '.py'
			if len(breakdown) > 2:
				args = ' '.join(breakdown[1:])
			else:
				args = ''

		if "help" in args:
			args = args.replace('help', '-h')

		generated_command = 'python3 ' + self.module_dir + '/' + module + ' ' + args
		#  print(generated_command) # Toggle for troubleshooting
		try:
			os.system(generated_command)
		except Exception as e:
			print(e)
			pass


if __name__ == '__main__':
	arguments = get_arguments()
	AEMUtility(arguments)

