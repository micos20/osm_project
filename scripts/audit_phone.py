#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import csv


def audit_phone(osm_file, output=False):
    '''
    Audit phone numbers
    
    Takes osm data file and returns:
    - list of tuples for all phone numbers (old number, formatted number)
    - list of problematic numbers which couldn't be formatted properly
    - list of numbers containing problematic characters
    - list of found area codes
    '''  
    # Selected  keys containing phone numbers
    phone_keys = ('phone', 'phone2', 'fax', 'contact:phone', 'contact:fax', 'communication:mobile')
    
    # Lists/ set to be filled and returned
    phone_numbers = []                       # list of tuples for all phone numbers (old number, formatted number)
    problematic_numbers = []                 # list of problematic numbers which couldn't be formatted properly
    special_chars = []                       # list of numbers containing problematic characters
    unique_area_codes = set()                # set tuples containing area codes and area name
    
    # Regex to find all phone numbers containing non-digit characters excluding '+' and ' ' 
    regex_special_chars = re.compile(r'[^\d+ ]')  
    
    # Read German area codes from csv into dict
    area_codes = read_area_codes('../data/NVONB.INTERNET.20200916.ONB.csv')     

    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in phone_keys:
            number = tag.get('v')
            
            # Check for non-numeric characters in phone numbers
            special = regex_special_chars.search(number)
            if special != None:
                special_chars.append(number)
            
            # Clean phone numbers
            new_number = update_phone(number, area_codes)
            if not new_number:
                problematic_numbers.append(number)
            else:
                phone_numbers.append( (number, new_number) )   
    
    # Extract unique area codes from phone_numbers list
    for item in phone_numbers:
        for nbr in item[1].split(';'):      # More than 1 number per key
            code = nbr.split()[1]
            unique_area_codes.add( (code, area_codes[code] ) )
        
    # Output
    if output == True:
        print("Nbr of phone numbers:", len(phone_numbers))
        print("Nbr of unique area codes:", len(unique_area_codes))
        print("Nbr of numbers containing non-digit characters:", len(special_chars))
        print("Nbr of problematic numbers (after cleaning):", len(problematic_numbers))
        print("Problematic numbers:")
        print(problematic_numbers)
    
    return phone_numbers, problematic_numbers, special_chars, unique_area_codes
            

def update_phone(nbr, area_codes):
    '''
    Takes phone numbers separated by ';' and area code dict.
    
    Returns properly formatted phone numbers acc. to ITU-T E.123, E.164
    
    If area code not found returns: False
    Currently only German area codes are implemented. When non German 
      county code is encountered function returns: False
    '''
    # Regex for extraction of German country code
    regex_country = re.compile(r'^ *((\+|00)49)')
    # Regex to remove all non-numeric characters from phone number (except '+')
    regex_special = re.compile(r'[^\d+]+')
    
    number_list = []                # List of return numbers per key (normally only 1 number)
    for number in nbr.split(';'):   # Consiering multiple numbers per key separated by ';' 
        # Remove non-numeric characters (except '+')   
        number = regex_special.sub('', number)
        
        # Extract country code
        country_match = regex_country.match(number)
        if country_match != None: 
            country = country_match.group(0)
            number = regex_country.sub('', number)              
        else:
            # Return False if not German country code
            return False
         
        # Extract area code from number
        code_found = False
        for i in range(2,6):        # Area code consists of 2 to 5 digits
            area = number[:i]       # area equals first i digits of number
            # Iterate over area codes of length i and compare to area extracted from number
            for code in (x for x in area_codes.keys() if len(x) == i):
                if area == code:
                    code_found = True
                    subscriber = number.replace(area, '')  # Remaining string of number is subscriber part
                    break
            if code_found == True: break 

        # Return False if no area code found
        if code_found == False:
            return False
        
        # Concatenate numbers found and cleaned
        number_list.append(country + " " + area + " " + subscriber)
            
    return ";".join(number_list)

def read_area_codes(file):
    '''
    Read German area codes from "file" and return a dict
    '''
    result = {}
    with open(file, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)        # Skip header
        for row in reader:
            result[row[0]] = row[1]
    return result
    
    
if __name__ == '__main__':
    # osm data files
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=20.osm'
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
    osm_file = '../data/GE_SH_PI_elmshorn_uetersen.osm'
    
    print("Audit & clean phone numbers:")
    print("Some statistics:")
    phnbr, problm, special, areas = audit_phone(osm_file, output=True)
    
    print("\n")
    print("Numbers containing special characters:")
    for number in special:
        print(number)
        
    print("\n")
    print("Number of found area codes: ", len(areas) )
    print("Area codes:")
    for code in sorted(areas):
        print("Area code: {0:>5d}, area name: {1}".format(int(code[0]), code[1]) )
    
    print("\n")
    print("Updated phone numbers (before, after):")
    for number in phnbr[100:110]:
        print(number)
    
        