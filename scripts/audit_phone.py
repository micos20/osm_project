#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import csv


def audit_phone(osm_file):
    # Selected  keys containing phone numbers
    phone_keys = ('phone', 'phone2', 'fax', 'contact:phone', 'contact:fax', 'communication:mobile')
    phone_numbers = []
    split_numbers = []
    not_GER = []
    area_code_not_found = []

    area_codes = read_area_codes('NVONB.INTERNET.20200916.ONB.csv')     

    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in phone_keys:
            number = tag.get('v')
            new_number = update_phone(number, area_codes)
            print(number, new_number)               
            
            
    return None
            

def update_phone(number, area_codes):
    
    regex_country = re.compile(r'^ *((\+|00)49)')
    regex_special = re.compile(r'[^\d]+')
    
    # Extract country code
    country_match = regex_country.match(number)
    if country_match != None: 
        country = country_match.group(0)
        number = regex_country.sub('', number)              
    else:
        return False
    
    # Remove non-numeric characters    
    number = regex_special.sub('', number)
    
    # Extract area code from number
    code_found = False
    area = ''
    for i in range(2,6):
        area = number[:i]
        for code in (x for x in area_codes.keys() if len(x) == i):
            if area == code:
                code_found = True
                subscriber = 'sub'
                break
        if code_found == True: break 

    if code_found == False:
        return False

    return country + " " + area + " " + subscriber

def read_area_codes(file):
    result = {}
    with open(file, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)        # Skip header
        for row in reader:
            result[row[0]] = row[1]
    return result