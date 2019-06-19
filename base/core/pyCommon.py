import sys
sys.path.append(".")
import os
import sys
import time
import platform
import argparse
from pathlib import Path
from os.path import basename
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit import PromptSession


# Global Variables
date = time.strftime("%m-%d-%y")  # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%I-%M")  # Time
exec_time = str(time.strftime("%I_%M_%p"))  # Time
home_path = str(Path.home())
current_dir = os.path.dirname(os.path.realpath(__file__))  # Get Current Directory of Running Script
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # Get Parent of Current Directory of Script
parent_of_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))  # Get Parent of Current Directory of Script
