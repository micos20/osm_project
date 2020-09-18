#!python
# -*- coding: utf-8 -*-
#
# ================================================== #
#            Wrangle Helper Functions                #
# ================================================== #

import csv
import codecs
import re
import xml.etree.cElementTree as ET
from datetime import datetime as dt, timedelta as td
import pytz
from dateutil import parser


def get_element(file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(file, events=('start', 'end'))
    _, root = next(context)        # omit osm element
    root.clear()
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            elem.clear()
            
def cast_type(value, value_type):
    """Return True when value can be casted to type 'value_type'. Else returns False"""
    valid_types = ('str', 'int', 'float', 'date') 
    if value_type not in valid_types:
        print("Wrong type: ", value_type)
        return None
    if value_type == 'float': 
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif value_type == 'str':
        try:
            str(value)
            return True
        except ValueError:
            return False
    elif value_type == 'int':
        try:
            int(value)
            return True
        except ValueError:
            return False    
    elif value_type == 'date':
        try:
            parser.parse(value)
            return True
        except:
            return False

def lookup_key(keys, search):
    '''
    Checks OSM key dict for 'search' pattern
    OSM key has the structure: {type: (key1, key1, key3, ...], ...}  
    Returns number the matching type:key values
    '''
    result = []
    for type in keys.keys():            
        for key in keys[type]:
            string = type + ":" + key
            if string.find(search) >= 0:
                result.append(string)
    return result

    