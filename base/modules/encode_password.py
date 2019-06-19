#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:
	Nick Serra <nick.serra@perficient.com>

Resources:
	https://gist.github.com/gowhari/fea9c559f08a310e5cfd62978bc86a1a

Summary:
	Encode and Decode passwords based on a key
"""
import sys
sys.path.append(".")
import getpass
import base64, six
from core.core.pyCommon import *


def encode_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-encode', '--encode', action='store', dest='encode_pass', required=False, help='Enter a password to Hash')
	parser.add_argument('-decode', '--decode', action='store', dest='decode_pass', required=False, help="Enter a hashed password to unHash")
	arguments = parser.parse_args()
	
	if not arguments.encode_pass:
		arguments.encode_pass = None
	if not arguments.decode_pass:
		arguments.decode_pass = None

	return arguments


class PasswordEncode:
	def __init__(self, arguments):
		self.key = 'DevOps'
		self.arguments = arguments
		self.suggestions = ['encode', 'decode', 'quit', 'exit']
		self.command_completer = WordCompleter(self.suggestions, ignore_case=True)
		# if not hasattr(self.arguments, 'encode_pass') and not hasattr(self.arguments, 'decode_pass'):
	
	def main(self):
		if self.arguments.encode_pass:
			encoded_password = self.encode(self.arguments.encode_pass)
			print('Encoded Password is:')
			print(encoded_password)
		elif self.arguments.decode_pass:
			decoded_password = self.decode(self.arguments.decode_pass.encode())
			print('Decoded Password is:')
			print(decoded_password)
		else:
			self.prompt()
			
	def prompt(self):
		print("\nInteractive Options:\n=====================")
		for option in self.suggestions:
			print(option)
		print("\n")
		session = PromptSession()
		while True:
			try:
				prompt_input = session.prompt('\nEncode Password > ', completer=self.command_completer)
			except KeyboardInterrupt:
				continue
			except EOFError:
				break
			else:
				if prompt_input.startswith('encode'):
					if len(prompt_input.split(' ')) > 1:
						password = prompt_input.split(' ')[1]
					else:
						password = None
					if not password:
						password = getpass.getpass('Please enter your Password: \n')
					encoded_password = self.encode(password)
					print('Encoded Password is:')
					print(encoded_password)
				elif prompt_input.startswith('decode'):
					if len(prompt_input.split(' ')) > 1:
						password = prompt_input.split(' ')[1]
					else:
						password = None
					if not password:
						password = getpass.getpass('Please enter your encoded Password: \n')
					decoded_password = self.decode(password)
					print('Decoded Password is:')
					print(decoded_password)
				elif prompt_input == "help":
					self.arguments.print_help()
				elif prompt_input == "quit" or prompt_input == 'exit':
					break
		
	def encode(self, string: str):
		key = str(self.key)
		encoded_chars = []
		for i in range(len(string)):
			key_c = key[i % len(key)]
			encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
			encoded_chars.append(encoded_c)
		encoded_string = ''.join(encoded_chars)
		encoded_string = encoded_string.encode('latin') if six.PY3 else encoded_string
		encoded_password = base64.urlsafe_b64encode(encoded_string).rstrip(b'=')
		return encoded_password
	
	def decode(self, string: str):
		key = self.key
		string = base64.urlsafe_b64decode(string.encode() + b'===')
		string = string.decode('latin') if six.PY3 else string
		encoded_chars = []
		for i in range(len(string)):
			key_c = key[i % len(key)]
			encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
			encoded_chars.append(encoded_c)
		decoded_string = ''.join(encoded_chars)
		return decoded_string
	

if __name__ == '__main__':
	arguments = encode_arguments()
	PasswordEncode(arguments).main()