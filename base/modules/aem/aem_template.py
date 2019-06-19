"""
AEM Template for Interactive Framework

Module Dependencies:
	sql_query
	encode_passwords

database/table dependencies:
	Environments_<Stack / Client>

"""
import sys
sys.path.append(".")
import json
from base.core.pyCommon import *
from base.modules.sql_query import sql_arguments, QueryDB
from base.modules.encode_password import PasswordEncode
# select * from 'Environments_FNA' where type like 'author';


class aemTemplate:
	def __init__(self):
		self.requirements = dict()
		self.output_dir = str(Path.home()) + os.sep + "aem_permission_reports"
		# print("Current Directory: " + str(current_dir))
		print("Output Directory: " + str(self.output_dir))

	def main(self):
		self.establish_requirements()
		self.decode_passwords(self.requirements)
		print(json.dumps(self.requirements, indent=4, sort_keys=True))

	def establish_requirements(self):
		x = 0
		query, headers, results = QueryDB().main()

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


if __name__ == '__main__':
	aemTemplate().main()
