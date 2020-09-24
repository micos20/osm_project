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
import requests
import json


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

def check_weblink(link):
    """
    Send http request to given url 
    Returns status of request:
        - True when no error occured (status code 200)
        - False when an error occured or the link is broken
    """   
    try:
        r = requests.head(link, timeout=4, allow_redirects=True)        
    except:
        return False    
    return r.status_code == requests.codes.ok    
    
def write_JSON(data, filename):
    '''
    Writes 'data' to 'filename' in JSON format. 
    'data' must be of type dict. The items get sorted by key name.
    Returns True if writing was successful, else returns False
    '''
    try:
        json.dump(data, open(filename, 'w'), sort_keys=True, indent=2)
    except:
        return False
    return True
    
def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def read_JSON(filename):
    pass
    