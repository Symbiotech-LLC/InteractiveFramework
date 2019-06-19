#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:
	grimmvenom <grimmvenom@gmail.com>

Module Dependencies:
	sql_query
	encode_passwords

SQLite database/table dependencies:
	Environments_<Stack / Client>

Summary:
1: Queries AEM Group Nodes
2: Queries AEM Account Nodes
3: Queries AEM Account Profile Nodes
4: Compares Accounts to Profiles
5: Compares Groups to Accounts
6: Merges results of comparisons
7: Writes Reports
	* Missing UUIDs
	* Missing Profiles
	* Permission Report for Audit
"""

import sys
sys.path.append(".")
import json
from base.core.pyCommon import *
from base.modules.sql_query import sql_arguments, QueryDB
from base.modules.encode_password import PasswordEncode
import requests
import glob, shutil, zipfile
import collections

# select * from 'Environments_FNA' where Type like 'author' and Environment like 'dev';


class aemPermissionReport:
	def __init__(self):
		self.arguments = None
		self.requirements = dict()
		self.output_dir = str(Path.home()) + os.sep + "aem_permission_reports"
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)
		self.report_name = None
		self.groups = None
		self.profiles = None
		self.accounts = None
		self.resolved_accounts = None
		self.accounts_without_profiles = None
		self.unresolved_group_uuid = None
		# print("Current Directory: " + str(current_dir))
		print("Output Directory: " + str(self.output_dir))

	def main(self):
		self.arguments = sql_arguments()
		self.establish_requirements()
		self.decode_passwords(self.requirements)
		# print(json.dumps(self.requirements, indent=4, sort_keys=True))

		for index, requirement in self.requirements.items():
			self.report_name = str(self.output_dir) + os.sep + requirement['Environment']
			self.groups = self.list_aem_groups(requirement)  # Get a List of AEM Group Nodes
			self.profiles = self.list_aem_profiles(requirement)  # Get a List of AEM Account Profile Nodes
			self.accounts = self.list_aem_accounts(requirement)  # Get a List of AEM Account Nodes
			self.resolved_accounts, self.accounts_without_profiles = self.resolve_identities(requirement)  # Associate User Profile Data to AEM Account
			self.unresolved_group_uuid = self.merge_results()  # Resolve UUIDs in Groups Memberships label
			self.build_reports(requirement)  # Write Report to a tsv file

	def establish_requirements(self):
		x = 0
		query, headers, results = QueryDB(self.arguments).main()
		print("Query: " + str(query))
		for requirement in results:
			x += 1
			if x not in self.requirements:
				self.requirements[x] = dict()
			for index, req in enumerate(requirement):
				req_header = headers[index]
				if not req_header in self.requirements[x]:
					self.requirements[x][req_header] = req

	def decode_passwords(self, dictionary):
		for index, requirement in dictionary.items():
			if requirement['Password']:
				encoded_pass = requirement['Password']
				print("Encoded: ", encoded_pass)
				class p:
					def __init__(self, x , y):
						decode_pass = x
						encode_pass = y
				args = p(str(encoded_pass), "")
				print("args ", args)
				decoded_pass = PasswordEncode(args).decode(encoded_pass)
				dictionary[index]['Password'] = str(decoded_pass)

	def list_aem_groups(self, requirement):  # Lookup AEM Group info
		print("\nListing " + requirement['Environment'] + " Groups")
		groups = {}
		if 'URL' in requirement:
			base_url = requirement['URL']
		elif 'IP' in requirement:
			base_url = 'https://' + requirement['IP']
		elif 'Hostname' in requirement:
			base_url = 'https://' + requirement['Hostname']
		else:
			base_url = None

		request_url = base_url + \
			"/bin/querybuilder.json?path=/home/groups&1_property=jcr:primaryType&1_property.value=rep:Group" + \
			"&p.hits=selective&p.properties=rep:principalName%20rep:authorizableId%20jcr:uuid%20jcr:path%20rep:members&p.limit=-1&orderby:path&orderby.sort=desc"

		print("Querying URL: " + request_url)
		headers = {'Expect': None}
		request = requests.get(request_url, headers=headers, auth=(requirement['Service Account'], requirement['Password']))
		status = request.status_code
		print("Status Code: " + str(status) + "\n")
		if status == 200:
			try:
				output = json.loads(request.text)
				for item in output['hits']:
					try:
						principal_name = item['rep:principalName']
					except:
						principal_name = ""
						pass
					try:
						path = item['jcr:path']
					except:
						path = ""
						pass
					try:
						uuid = item['jcr:uuid']
					except:
						uuid = ""
						pass
					try:
						auth_id = item['rep:authorizableId']
					except:
						auth_id = ""
						pass
					try:
						members = item['rep:members']
					except:
						members = []
						pass
					groups[principal_name] = {"path": path, "uuid": uuid, "authId": auth_id, "members": members}
					groups = dict(collections.OrderedDict(sorted(groups.items())))
			except Exception as e:
				print("Issue retrieving Results: " + str(e))
				groups = {}
				pass

			# print("Groups: \n" + str(groups))
			return groups

	def list_aem_accounts(self, requirement):  # Lookup AEM Account info
		print("\nListing " + requirement['Environment'] + " Users")
		accounts = {}
		if 'URL' in requirement:
			base_url = requirement['URL']
		elif 'IP' in requirement:
			base_url = 'https://' + requirement['IP']
		elif 'Hostname' in requirement:
			base_url = 'https://' + requirement['Hostname']
		else:
			base_url = None
		request_url = base_url + \
			"/bin/querybuilder.json?path=/home/users&1_property=jcr:primaryType&1_property.value=rep:User" + \
			"&p.hits=selective&p.properties=rep:principalName%20rep:authorizableId%20givenName%20familyName%20email%20" + \
			"jcr:uuid%20jcr:path&p.limit=-1&orderby:path&orderby.sort=desc"

		print("Querying URL: " + request_url)
		headers = {'Expect': None}
		request = requests.get(request_url, headers=headers, auth=(requirement['Service Account'], requirement['Password']))
		status = request.status_code
		print("Status Code: " + str(status) + "\n")
		if status == 200:
			count = 0
			output = json.loads(request.text)
			for item in output['hits']:
				count += 1
				try:
					path = item['jcr:path']
				except:
					path = count
					pass
				try:
					principal_name = item['rep:principalName']
				except:
					principal_name = ""
					pass
				try:
					uuid = item['jcr:uuid']
				except:
					uuid = ""
					pass
				try:
					auth_id = item['rep:authorizableId']
				except:
					auth_id = ""
					pass

				accounts[uuid] = {"uuid": uuid, "accountName": principal_name, "authId": auth_id, "path": path}
				users = dict(collections.OrderedDict(sorted(accounts.items())))

			# print("Users: \n" + str(users))
			return accounts

	def list_aem_profiles(self, requirement):  # Lookup AEM User Profile Info
		print("Lookup AEM Profile")
		profiles = {}
		if 'URL' in requirement:
			base_url = requirement['URL']
		elif 'IP' in requirement:
			base_url = 'https://' + requirement['IP']
		elif 'Hostname' in requirement:
			base_url = 'https://' + requirement['Hostname']
		else:
			base_url = None

		request_url = base_url + "/bin/querybuilder.json?path=/home/users&nodename=profile&1_property=jcr:primaryType&1_property.value=nt:unstructured&1_property.operation=like&p.hits=full&p.limit=-1"
		print("Querying URL: " + request_url)
		headers = {'Expect': None}
		request = requests.get(request_url, headers=headers, auth=(requirement['Service Account'], requirement['Password']))
		status = request.status_code
		print("Status Code: " + str(status) + "\n")
		if status == 200:
			count = 0
			output = json.loads(request.text)
			for item in output['hits']:
				count += 1
				try:
					path = item['jcr:path']
				except:
					path = count
					pass
				try:
					first_name = item['givenName']
				except:
					first_name = ""
					pass
				try:
					last_name = item['familyName']
				except:
					last_name = ""
					pass
				try:
					email = item['email']
				except:
					email = ""
					pass
				profiles[path.replace("/profile", "")] = {"firstName": first_name, "lastName": last_name, "email": email, "path": path}
			return profiles

	def resolve_identities(self, requirement):  # Associate AEM Profile nodes with AEM Account Nodes
		resolved_accounts = {}
		accounts_without_profiles = {}
		for account, data in self.accounts.items():
			path = data['path']
			try:
				identities = self.profiles[path]
				# print(identities)
				first_name = self.profiles[path]['firstName']
				last_name = self.profiles[path]['lastName']
				email = self.profiles[path]['email']
				data['firstName'] = first_name
				data['lastName'] = last_name
				data['email'] = email
				# resolved_accounts[data['accountName']] = data
				resolved_accounts[account] = data
			except Exception as e:
				# print("Issue resolving " + account  + " : " + str(e))
				data['firstName'] = ""
				data['lastName'] = ""
				data['email'] = ""
				resolved_accounts[account] = data
				accounts_without_profiles[data['accountName']] = data
		print(" ")

		return resolved_accounts, accounts_without_profiles

	def merge_results(self):  # Associate Resolved Accounts with AEM Group Membership UUIDs
		unresolved_group_uuid = {}
		for group, data in self.groups.items():
			# print("Group: " + str(group))
			resolved_members = {}
			unresolved_uuids = []
			for member in data['members']:
				try:
					member_data = self.resolved_accounts[member]
					account_name = self.resolved_accounts[member]['accountName']
					# print("Member: " + account_name + "  " + str(member_data))
					resolved_members[account_name] = member_data
				except:
					unresolved_uuids.append(member)
					# print("Member data not found: " + str(member))
					pass
			unresolved_group_uuid[group] = unresolved_uuids
			self.groups[group]['members'] = resolved_members
		return unresolved_group_uuid

	def build_reports(self, requirement):
		if 'URL' in requirement:
			base_url = requirement['URL']
		elif 'IP' in requirement:
			base_url = 'https://' + requirement['IP']
		elif 'Hostname' in requirement:
			base_url = 'https://' + requirement['Hostname']
		else:
			base_url = None

		print("Building Report for " + str(base_url))
		print(" ")
		# Build Regular Group / Memberships report with AEM Account Contact Info
		audit_report2 = self.report_name + "-AEM-Audit-Normalized_" + str(date) + ".tsv"
		audit_report = self.report_name + "-AEM-Audit_" + str(date) + ".tsv"
		missing_uuids_report = self.report_name + "-Missing-UUIDs_" + str(date) + ".tsv"
		missing_profiles_report = self.report_name + "-Missing-Profiles_" + str(date) + ".tsv"
		AEM_Accounts = self.report_name + "-AEM-Accounts_" + str(date) + ".tsv"

		# Write Regular Audit Report
		tsv_file = open(audit_report2, 'w')
		tsv_file.write("AEM URL: " + str(base_url) + "\n\n")
		tsv_file.write("Group Name" + "\t" + "Group AEM Path" + "\t" + "AEM Account Name" + "\t" + \
			"First & Last Name" + "\t" + "Email Address" + "\t" + "AEM Path" + "\n\n")
		for group, data in self.groups.items():
			tsv_file.write(group + "\t" + data['path'] + "\n")
			for member, member_data in data['members'].items():
				tsv_file.write("\t\t" + str(member_data['accountName']) + "\t" + \
					str(member_data['firstName']) + " " + str(member_data['lastName']) + \
					"\t" + str(member_data['email']) + "\t" + str(member_data['path']) + "\n")
			tsv_file.write("\n\n")
		tsv_file.close()

		# Write unNormalized Audit Report
		tsv_file = open(audit_report, 'w')
		tsv_file.write("AEM URL: " + str(base_url) + "\n\n")
		tsv_file.write("Full Group Name" + "\t" + "Group Area" + "\t" + "Group Type" + "\t" + \
			"FirstName" + "\t" + "LastName" + "\t" + "E-mail Address" + "\t" + "CDSID" + "\t" + "UUID" + "\t" + "User Info" + "\n")
		for group, data in self.groups.items():
			if "-" in group:
				group_area = group.split("-", 1)[0]
				group_type = group.split("-", 1)[1]
			else:
				group_area = group
				group_type = group
			for member, member_data in data['members'].items():
				full_name = member_data['firstName'] + " " + member_data['lastName']
				tsv_file.write(str(group) + "\t" + str(group_area) + "\t" + str(group_type) + "\t" + \
					str(member_data['firstName']) + "\t" + str(member_data['lastName']) + \
					"\t" + str(member_data['email']) + "\t" + str(member_data['accountName']) + "\t" + str(member_data['uuid']) + \
					"\t" + str(full_name) + " (" + str(member_data['email']) + ") (" + str(
					member_data['accountName']) + ")\n")
		# tsv_file.write("\n\n")
		tsv_file.close()

		# Write Report of Missing UUIDs from Group Memberships
		tsv_file = open(missing_uuids_report, 'w')
		tsv_file.write("AEM URL: " + str(base_url) + "\n\n")
		tsv_file.write("Group Name" + "\t" + "Missing UUID" + "\n\n")
		for group, data in self.unresolved_group_uuid.items():
			tsv_file.write(group + "\n")
			for uuid in data:
				tsv_file.write("\t" + str(uuid) + "\n")
			tsv_file.write("\n")
		tsv_file.close()

		# Write Report of Accounts Missing Profiles
		tsv_file = open(missing_profiles_report, 'w')
		tsv_file.write("AEM URL: " + str(base_url) + "\n\n")
		tsv_file.write(
			"AEM Account Name" + "\t" + "AEM Path" + "\t" + "UUID" + "\t" + "First Name" + "\t" + "Last Name" + "\t" + "Email Address" + "\n\n")
		for account, data in self.accounts_without_profiles.items():
			tsv_file.write(
				str(account) + "\t" + str(data['path']) + "\t" + str(data['uuid']) + "\t" + str(data['firstName']) + \
				"\t" + str(data['lastName']) + "\t" + str(data['email']) + "\n")
		tsv_file.close()

		# Write Report of AEM Accounts
		tsv_file = open(AEM_Accounts, 'w')
		tsv_file.write("AEM URL: " + str(base_url) + "\n\n")
		tsv_file.write(
			"AEM Account Name" + "\t" + "First Name" + "\t" + "Last Name" + "\t" + "Email Address" + "\t" + "AEM Path" + "\t" + "UUID""\n\n")
		for account, data in self.resolved_accounts.items():
			tsv_file.write(
				str(data['accountName']) + "\t" + str(data['firstName']) + "\t" + str(data['lastName']) + \
				"\t" + str(data['email']) + "\t" + str(data['path']) + "\t" + str(data['uuid']) + "\n")
		tsv_file.close()


if __name__ == '__main__':
	aemPermissionReport().main()
