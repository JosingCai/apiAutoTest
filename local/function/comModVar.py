#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import requests
import shutil
import argparse
import datetime
import time
import random
import json
import yaml
import threading
import  xml.dom.minidom
import xlwt
import xlrd
import importlib
import pymysql

if sys.version > '3':
    import subprocess as commands
    import configparser as ConfigParser
    from imp import reload
    reload(sys)
else:
    import commands
    import ConfigParser
    reload(sys)
    sys.setdefaultencoding('utf-8')

from itertools import product
from collections import Counter
from xlutils.copy import copy as xl_copy

# Log level
DEBUG = True

# Path to storage files
sourceFPath = "HTML"
configPath = "Config"
CSVPath = "CSV"
LogPath = "LOG"

true = "true"
false = "false"
today = datetime.datetime.now().strftime('%Y-%m-%d')
curPath = os.getcwd()

hConfig = "TestHost.ini"

modules = {"DAVINCI": 9080, "RBAC":9082, "XMDB":8080, "FLOW":8083, "SRV":8088, "BOOT": 9090, "ACT2": 8080}

PROTOCOL = "http"