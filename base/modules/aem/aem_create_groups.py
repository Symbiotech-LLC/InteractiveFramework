#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author:
	grimmvenom <grimmvenom@gmail.com>

Module Dependencies:
	sql_query
	encode_passwords

SQLite database/table dependencies:
	Environments_<Stack / Client>
	Groups_<Stack / Client>
	Service_Accounts_<Stack / Client>

Summary:
	Module to automate AEM Group Creation
		System Groups
		Tenant / Domain Groups
		Application Groups
		Deployment User


# run aem_create_groups --db "AEM.db" --query 'select * from "Environments_FNA" where Type like "author" and Environment like "dev";' --app testApp --tenant testTenant --system --execute

"""

import sys
sys.path.append(".")
import json
import requests
from base.core.pyCommon import *
from base.modules.sql_query import sql_arguments, QueryDB
from base.modules.encode_password import PasswordEncode
# select * from 'Environments_FNA' where type like 'author';


def logging():
	log_dir = home_path + os.sep + 'aem_create_groups' + os.sep + 'logs'
	pylog = log_dir + "/" + "Log_GroupCreator-" + date + "_" + Time + ".txt"
	# Create the folder if it doesn't exist already.
	if not os.path.exists(log_dir):
		print(log_dir + "Does Not Exist....... Creating Directory")
		os.makedirs(log_dir)
	class Tee(object):
		def __init__(self, *files):
			self.files = files

		def write(self, obj):
			for f in self.files:
				f.write(obj)
				f.flush() # If you want the output to be visible immediately

		def flush(self):
			for f in self.files:
				f.flush()

	pyout = open(pylog, 'w')
	# original = sys.stdout
	sys.stdout = Tee(sys.stdout, pyout)


def aem_group_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('--database', '--db', '-database', '-db', action='store', dest='database', required=False, help='Enter path to sqlite database')
	parser.add_argument('--query', '--q', '-query', '-q', action='store', dest='query', required=False, help='Enter SQLite query for environment requirements')
	parser.add_argument('--tenant', '-tenant', '--t', '-t', action='store', dest='tenant', required=False, help='Enter name of tenant')
	parser.add_argument('--app', '-app', '-a', '--a', action='store', dest='app', required=False, help='Enter name of application')
	parser.add_argument('--system', '-system', '--s', '-s', action='store_true', dest='system', required=False, help='Create system utility groups')
	parser.add_argument('--execute', '-execute', '--e', '-e', '--create_group', '-create_group', '--cg', '-cg',
		action='store_true', dest='execute', required=False, help='Trigger Group Creation instead of starting in prompt')
	arguments = parser.parse_args()

	if not arguments.database:
		arguments.database = input('\nWhat is the path to your sqlite database?:\n')

	if os.path.exists(arguments.database):
		arguments.database = str(arguments.database)
	elif os.path.exists(parent_of_parent_dir + os.sep + 'database' + os.sep + arguments.database):
		arguments.database = parent_of_parent_dir + os.sep + 'database' + os.sep + str(arguments.database)
	else:
		print(arguments.database + " does NOT exist")
		exit()

	if not arguments.query:
		arguments.query = None
	if not arguments.tenant:
		arguments.tenant = None
	if not arguments.app:
		arguments.app = None
	if not arguments.system:
		arguments.system = False
	if not arguments.execute:
		arguments.execute = False

	return arguments


class aemGroups:
	def __init__(self, arguments):
		self.arguments = arguments
		self.suggestions = ['show commands', 'show variables', 'set app', 'set tenant', 'set system',
			'set environments', 'create groups', 'quit', 'exit', 'help', ]
		self.command_completer = WordCompleter(self.suggestions, ignore_case=True)
		self.requirements = dict()
		self.secure_requirements = dict()
		self.available_tables = list()
		self.utility_data = dict()
		self.app_groups = dict()
		self.tenant_groups = dict()
		self.system_groups = dict()
		if self.arguments.query:
			self.establish_requirements()  # Query for environments / servers to run module on
			self.decode_passwords(self.requirements)  # Decode Environment service account passwords
		self.status_success = [200, 201, 301, 302]

	def main(self):
		self.available_tables = QueryDB(self.arguments).show_tables()  # Save list of available tables
		if self.arguments.execute:
			if self.arguments.system or self.arguments.tenant or (self.arguments.tenant and self.arguments.app):
				self.run()
			else:
				print("\nNecessary Fields not filled out to execute.... Sending to Prompt")
				self.prompt()
		else:
			self.prompt()

	def prompt(self):
		session = PromptSession()
		while True:
			try:
				prompt_input = session.prompt('\nAEM Create Groups > ', completer=self.command_completer)
			except KeyboardInterrupt:
				continue
			except EOFError:
				break
			else:
				if prompt_input == "quit" or prompt_input == 'exit':
					break
				elif prompt_input == 'show variables':
					print("\nVariables\n================================")
					self.define_group_requirements()
					print("System: ", self.arguments.system)
					print(json.dumps(self.system_groups, indent=4, sort_keys=False))
					print(" ")
					print("Tenant: ", self.arguments.tenant)
					print(json.dumps(self.tenant_groups, indent=4, sort_keys=False))
					print(" ")
					print("App: ", self.arguments.app)
					print(json.dumps(self.app_groups, indent=4, sort_keys=False))
					print(" ")
					print("Environment Requirements: ")
					print(json.dumps(self.secure_requirements, indent=4, sort_keys=False))
				elif prompt_input == 'show commands' or prompt_input == 'help':
					print("\nCommands\n================================")
					for command in self.suggestions:
						print(command)
				elif 'set app' in prompt_input:
					if len(prompt_input.split(' ')) > 2:
						app_name = prompt_input.split(' ')[2]
						self.arguments.app = app_name
					else:
						self.arguments.app = input('\nWhat is the name of the app?\n')
				elif 'set tenant' in prompt_input:
					if len(prompt_input.split(' ')) > 2:
						tenant_name = prompt_input.split(' ')[2]
						self.arguments.tenant = tenant_name
					else:
						self.arguments.tenant = input('\nWhat is the name of the tenant?\n')
				elif prompt_input == 'set system':
					if self.arguments.system == False:
						self.arguments.system = True
					elif self.arguments.system == True:
						self.arguments.system = False
						self.system_groups = dict()

				elif prompt_input == 'set environments':
					self.establish_requirements()  # Query for environments / servers to run module on
					self.decode_passwords(self.requirements)  # Decode Environment service account passwords
				elif prompt_input == 'create groups':
					if self.arguments.app and not self.arguments.tenant:
						print("\nCannot have an application without a tenant.")
						print("Please use the 'set tenant' command")
					else:
						self.run()
						self.reset()

	def reset(self):  # Reset variables to nothing to be able to run a fresh onboarding
		self.system_groups = dict()
		self.tenant_groups = dict()
		self.app_groups = dict()
		self.utility_data = dict()
		# self.requirements = dict()  # Toggle Comment to clear defined environments

	def establish_requirements(self):  # Figure out which environments to loop through and create groups for
		x = 0
		query, headers, results = QueryDB(self.arguments).main()
		for requirement in results:
			x += 1
			if x not in self.requirements:
				self.requirements[x] = dict()
			if x not in self.secure_requirements:
				self.secure_requirements[x] = dict()
			for index, req in enumerate(requirement):
				req_header = headers[index]
				if not req_header in self.requirements[x]:
					self.requirements[x][req_header] = req
				if not req_header in self.secure_requirements[x] and req_header != 'Password':
					self.secure_requirements[x][req_header] = req

	def decode_passwords(self, dictionary):  # Decode passwords from queries
		for index, requirement in dictionary.items():
			if requirement['Password']:
				encoded_pass = requirement['Password']
				class p:
					def __init__(self, x , y):
						decode_pass = x
						encode_pass = y
				args = p(str(encoded_pass), "")
				decoded_pass = PasswordEncode(args).decode(encoded_pass)
				dictionary[index]['Password'] = str(decoded_pass)

	def define_group_requirements(self):  # Loop through tables and define groups that need to be created
		table_to_query = dict()
		self.system_groups = dict()
		self.tenant_groups = dict()
		self.app_groups = dict()
		self.utility_data = dict()
		for table in self.available_tables:
			if 'Groups' in table:
				table_to_query['app'] = list()
				table_to_query['app'].append(table)
			elif 'Service_Accounts' in table:
				table_to_query['utility'] = list()
				table_to_query['utility'].append(table)

		if len(table_to_query['app']) > 1:  # If multiple group tables, select one
			for index, table in enumerate(table_to_query['app']):
				print(index, ": ", table)
			number = input('Multiple tables found, which do you wish to use?:\n')
			app_query = str(table_to_query['app'][number])
		else:
			app_query = str(table_to_query['app'][0])

		if len(table_to_query['utility']) > 1:  # If multiple utility tables, select one
			for index, table in enumerate(table_to_query['utility']):
				print(index, ": ", table)
			number = input('Multiple tables found, which do you wish to use?:\n')
			utility_query = str(table_to_query['utility'][number])
		else:
			utility_query = str(table_to_query['utility'][0])

		if self.arguments.system:  # Get System Group / User Requirements
			query = 'select * from ' + app_query + ' where Type like \'system\';'
			self.define_dictionary_results(query, self.system_groups)
		if self.arguments.tenant:  # Get Tenant Group / User Requirements
			query = 'select * from ' + app_query + ' where Type like \'tenant\';'
			self.define_dictionary_results(query, self.tenant_groups)
		if self.arguments.app:  # Get App Group / User Requirements
			query = 'select * from ' + app_query + ' where Type like \'app\';'
			self.define_dictionary_results(query, self.app_groups)
		# Get Service Account / Utility Passwords
		query = 'select * from ' + utility_query + ';'
		self.define_dictionary_results(query, self.utility_data)
		self.decode_passwords(self.utility_data)

	def define_dictionary_results(self, query, var):  # Perform query and add data to dictionary
		query, title, all_results = QueryDB(self.arguments).query(query)
		x = 0
		for result in all_results:
			x += 1
			for index, r in enumerate(result):
				if var == self.app_groups or var == self.tenant_groups:
					if title[index] == 'Name' or title[index] == 'Member_Of':
						if self.arguments.app:
							r = r.replace('app', self.arguments.app)
						if self.arguments.tenant:
							r = r.replace('tenant', self.arguments.tenant)

				if title[index] == 'Member_Of':
					r = r.split(',\n')
				if len(r) >= 1 and (type(r) != list() and len(r[0]) >= 1):
					if x not in var:
						var[x] = dict()
					if not title[index] in var[x]:
						var[x][title[index]] = r

	def determine_url(self, requirement):
		if 'URL' in requirement.keys():
			url = requirement['URL']
		elif 'IP' in requirement.keys():
			url = 'https://' + str(requirement['IP'])
		elif 'Hostname' in requirement.keys():
			url = 'https://' + str(requirement['Hostname'])
		else:
			print("No Server Data Specified")
			url = None
		return url

	def create_aem_group(self, requirement, group_name):
		url = self.determine_url(requirement)
		if url:
			aem_user = requirement['Service Account']
			aem_password = requirement['Password']
			print("Querying AEM For PreExisting Group: " + group_name)
			# request_groups = url + "/bin/querybuilder.json?path=/home/groups&1_property=jcr:primaryType&1_property.value=rep:Group&p.hits=selective&p.properties=rep:authorizableId&p.limit=-1"  # Old 6.1 Query
			request_groups = url + "/bin/querybuilder.json?path=/home/groups&1_property=jcr:primaryType&1_property.value=rep:Group&p.hits=selective&p.properties=rep:authorizableId" + \
				"&2_property=rep:authorizableId&2_property.value=" + str(group_name) + "&p.hits=full&p.limit=-1"
			print(request_groups)
			request = requests.get(request_groups, auth=(aem_user, aem_password))
			status = request.status_code
			print("Status: " + str(status))
			print("-----------------")
			output = json.loads(request.text)
			# print(output)

			if group_name not in json.dumps(output):
				print(group_name + " not found")
				print("Creating group: " + group_name)

				request_url = url + "/libs/granite/security/post/authorizables"
				# print("Sending Request to: " + url)

				headers = {'Expect': None, 'createGroup': group_name, 'authorizableId': group_name}
				data = {'createGroup': group_name, 'authorizableId': group_name}
				# Sends Request to Add User to Group in AEM
				request = requests.post(request_url, headers=headers, data=data, auth=(aem_user, aem_password))
				status = request.status_code
				print("Request Status: " + str(status))
				if status not in self.status_success:
					print(request.text)
				print(" ")
			else:
				print(group_name + " already exists")
				print(" ")

	def create_aem_user(self, requirement, user_name):
		url = self.determine_url(requirement)
		jpassword = None
		for index, item in self.utility_data.items():
			if item['Environment'] == requirement['Environment']:
				jpassword = item['Environment']
				break
		# jpassword = self.utility_data[requirement['Environment']]['Password']

		if url:
			aem_user = requirement['Service Account']
			aem_password = requirement['Password']
			print("\nQuerying AEM For PreExisting user: " + user_name)
			# request_users = url + "/bin/querybuilder.json?path=/home/users&nodename=" + user_name + "&limit=-1"  # Old 6.1 query
			request_users = url + "/bin/querybuilder.json?path=/home/users&1_property=jcr:primaryType&1_property.value=rep:User&" + \
			                "2_property=rep:authorizableId&2_property.value=" + str(user_name) + "&p.hits=full&p.limit=-1"
			print("url: " + request_users)
			request = requests.get(request_users, auth=(aem_user, aem_password))
			status = request.status_code
			print("Status: " + str(status))
			print("-----------------")
			output = json.loads(request.text)
			# print(output)

			if user_name not in json.dumps(output):
				print(user_name + " not found")
				print("Creating group: " + user_name)

				request_url = url + "/libs/granite/security/post/authorizables"
				# print("Sending Request to: " + url)

				headers = {'Expect': None}
				data = {'createUser': user_name, 'authorizableId': user_name, 'rep:password': jpassword,
					'profile/givenName': user_name, 'profile/familyName': user_name}
				# Sends Request to Add User to Group in AEM
				request = requests.post(request_url, headers=headers, data=data, auth=(aem_user, aem_password))
				status = request.status_code
				print("Request Status: " + str(status))
				if status not in self.status_success:
					print(request.text)
				print(" ")
			else:
				print(user_name + " already exists")
				print(" ")

	def add_targetGroup_to_parentGroup(self, requirement, target_group, parent_group):
		url = self.determine_url(requirement)
		print("\nAdding " + target_group + " to " + parent_group)
		if url:
			aem_user = requirement['Service Account']
			aem_password = requirement['Password']
			# Find Group PATH
			detection_url = url + "/bin/querybuilder.json?path=/home/groups&1_property=jcr:primaryType&1_property.value=rep:Group" + \
				"&p.properties=rep:authorizableId&2_property=rep:authorizableId&2_property.value=" + \
				parent_group + "&p.hits=full&p.limit=-1"
			request = requests.get(detection_url, auth=(aem_user, aem_password))
			status = request.status_code
			print("Status: " + str(status))
			print("-----------------")
			output = json.loads(request.text)

			# print(output)
			if output['results'] >= 1 and 'hits' in output.keys():
				result = output['hits']
				path = result[0]['jcr:path']
				print("Path: ", path)

				# Add Memberships
				# request_url = url + "/home/groups/" + parent_group[0] + "/" + parent_group + ".rw.html"  # Old 6.0 method
				request_url = url + path + ".rw.html"
				print("Sending Request to: " + request_url)

				headers = {'Expect': None, 'addMembers': target_group}
				data = {'addMembers': target_group}
				# Sends Request to Add User to Group in AEM
				request = requests.post(request_url, headers=headers, data=data, auth=(aem_user, aem_password))
				status = request.status_code
				print("Request Status: " + str(status))
				if status not in self.status_success:
					print(request.text)
				print(" ")

	def run(self):  # Loop through requirements and perform creations
		run_system = False
		run_tenant = False
		run_app = False
		self.define_group_requirements()
		for index, requirement in self.requirements.items():
			print("Starting Creation for:")
			print(self.secure_requirements[index])
			print("===================================")
			if self.arguments.system:  # Create System Groups
				run_system = True
				for index, group_req in self.system_groups.items():
					# print(group_req)
					if group_req['Node_Type'] == 'group':
						self.create_aem_group(requirement, group_req['Name'])
					elif group_req['Node-Type'] == 'user':
						self.create_aem_user(requirement, group_req['Name'])
				print(" ")
			if self.arguments.tenant:  # Create Tenant Groups
				run_tenant = True
				for index, group_req in self.tenant_groups.items():
					# print(group_req)
					if group_req['Node_Type'] == 'group':
						self.create_aem_group(requirement, group_req['Name'])
					elif group_req['Node-Type'] == 'user':
						self.create_aem_user(requirement, group_req['Name'])
				print(" ")
			if self.arguments.tenant and self.arguments.app:  # Create App Groups
				run_app = True
				for index, group_req in self.app_groups.items():
					# print(group_req)
					if group_req['Node_Type'] == 'group':
						self.create_aem_group(requirement, group_req['Name'])
					elif group_req['Node_Type'] == 'user':
						self.create_aem_user(requirement, group_req['Name'])
				print(" ")
			else:
				print("App Groups can't be created without tenant groups")

			# Add Group Memberships
			if run_system:
				for index, data in self.system_groups.items():
					if 'Member_Of' in data.keys():
						print(data)
						name = data['Name']
						memberships = data['Member_Of']
						for membership in memberships:
							self.add_targetGroup_to_parentGroup(requirement, name, membership)
							time.sleep(1)
			if run_tenant:
				for index, data in self.tenant_groups.items():
					if 'Member_Of' in data.keys():
						print(data)
						name = data['Name']
						memberships = data['Member_Of']
						for membership in memberships:
							self.add_targetGroup_to_parentGroup(requirement, name, membership)
							time.sleep(1)
			if run_tenant and run_app:
				for index, data in self.app_groups.items():
					if 'Member_Of' in data.keys():
						print(data)
						name = data['Name']
						memberships = data['Member_Of']
						for membership in memberships:
							self.add_targetGroup_to_parentGroup(requirement, name, membership)
							time.sleep(1)


if __name__ == '__main__':
	args = aem_group_arguments()
	logging()
	aemGroups(args).main()
