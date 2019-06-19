# -*- coding: utf-8 -*-
"""
Summary:
		Utility to automate various AEM processes and Reports

author:
Nick Serra <nick.serra@perficient.com>

"""

from base.main import AEMUtility
from base.core.get_arguments import *

if __name__ == '__main__':
	arguments = get_arguments()
	AEMUtility(arguments)
