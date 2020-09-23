#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re
import xml.etree.cElementTree as ET

def audit_phone(osm_file):
    # Selected  keys containing phone numbers
    phone_keys = ('phone', 'phone2', 'fax', 'contact:phone', 'contact:fax', 'communication:mobile')
    phone_numbers = []

    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in phone_keys:
            phone_numbers.append(tag.get('v'))

    return phone_numbers
            
