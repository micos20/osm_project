#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type, check_weblink, write_JSON
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import requests

def weblinks_by_key(osm_file):
    '''
    Identify weblinks by given keys (OSM recommendation)
    Returns two dicts containing weblinks and badlinks
    '''
    webkeys = {'website', 'url', 'image', 'wikipedia'}      # keys containing weblinks suggested by OSM
    weblinks = defaultdict(list)                            # Dict containing weblinks
    badlinks = defaultdict(list)                            # Dict containing bad links
    # Regex to match a weblink (intended to identify bad links)
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')

    # Parsing the file (only tags)
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if webkeys.intersection(tag.get('k').split(':')):
            weblinks[tag.get('k')].append(tag.get('v'))
            match = regex_weblink.match(tag.get('v'))
            if match == None:
                badlinks[tag.get('k')].append(tag.get('v'))
    
    # Output summary    
    print("Found weblinks in:")
    for key in weblinks:
        print("  " + key + ":", len(weblinks[key]))
    
    print("\nFound bad links in:")
    for key in badlinks:
        print("  " + key + ":", len(badlinks[key]))
    
    return weblinks, badlinks
    
def weblinks_by_value(osm_file):   
    '''
    Parses node, way and relation tags and checks keys for weblinks
    Returns a dict containing found weblinks
    ''' 
    weblinks = defaultdict(list)                # Dict for found weblinks
    # This time we use the regex to identify weblinks in other keys
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')

    # Parsing the file (only tags)
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        match = regex_weblink.match(tag.get('v'))
        if match != None:
            weblinks[tag.get('k')].append(tag.get('v'))
    
    #Output
    print("Found weblinks:")
    for key in weblinks:
        print("  " + key + ":", len(weblinks[key]))
        
    return weblinks
    
def check_url(osm_file, output=False, JSON_out=False):
    '''
    This function parses the OSM file and checks the tags for weblinks.
    Identified weblinks are send to 'update_webkey' function.
    On request a look-up table is written to a JSON file mapping the current url to the updated.
    '''
    # The following keys will be checked for weblinks
    webkeys     = ['website', 'url', 'image', 'removed:website', 'contact:website', 
                   'source', 'contact:facebook', 'internet_access:ssid', 'note']
    # Regex to match a weblink
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')
    
    weblink_LUT = {}                # Dict mapping current url to checked/working url
    stats = defaultdict(list)       # Collect some statistics
    
    # Parsing the file
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in webkeys:         # Is valid key to be checked?
            match = regex_weblink.match(tag.get('v'))           
            if match != None:               # Next tag if not a weblink
                url = match.group(0)
                # Weblink already checked?
                if weblink_LUT.get(url, False):     
                    stats['doublicate'].append(url)
                    continue
                elif weblink_LUT.get(url.rstrip('/'), False):
                    weblink_LUT[url] = weblink_LUT[url.rstrip('/')]
                    stats['doublicate'].append(url)
                    continue
                elif weblink_LUT.get(url + '/', False):
                    weblink_LUT[url] = weblink_LUT[url + '/']
                    stats['doublicate'].append(url)
                    continue
                # If not already checked check link now
                else:
                    new_url = update_webkey(match, weblink_LUT)
       
    # Fill stats dict with weblink statistics
    for oldlink, newlink in weblink_LUT.items():
        if newlink == False:
            stats['broken links'].append(oldlink)
            continue               
            
        if oldlink.find('https:') == 0:
            stats['old secure links'].append(oldlink)
        elif oldlink.find('http:') == 0:
            stats['old insecure links'].append(oldlink)
        else:
            stats['old undef links'].append(oldlink)
        
        if newlink.find('https:') == 0:
            stats['new secure links'].append(newlink)
        else:
            stats['new insecure links'].append(newlink)
                   
        old_sub = regex_weblink.match(oldlink).group(4).strip('/')
        new_sub = regex_weblink.match(newlink).group(4).strip('/')
        
        if old_sub != new_sub:
            stats['modified links'].append( (oldlink, newlink) )
    
    # Output
    if output == True:              
        # print stats
        print("Nbr insecure urls:  old/{:>4d}   new/{:>4d}".format(len(stats['old insecure links']), len(stats['new insecure links'])))
        print("Nbr secure urls:    old/{:>4d}   new/{:>4d}".format(len(stats['old secure links']), len(stats['new secure links'])))
        print("Nbr missing schemes: {:>4d}".format(len(stats['old undef links'])))
        print("Nbr modified links:  {:>4d}".format(len(stats['modified links'])))
        print("Nbr broken links:    {:>4d}".format(len(stats['broken links'])))
        print("Ndr of doublicates:  {:>4d}".format(len(stats['doublicate'])))
            
    # On request write JSON LUT file
    if JSON_out != False:
        if not write_JSON(weblink_LUT, JSON_out):
            print("JSON output went wrong!")
        else:
            print("JSON output successful!")
        
    return weblink_LUT, stats
        
        
def update_webkey(match, lut={}):                  
    '''
    Checks url (match object) if it works or tries to modify the url to make it work.
    Return: Updates look-up table (lut) mapping old and new url
    '''
    # Regex to modify path part of url
    reg = re.compile(r'/[^/]*$')            
    
    # sublink contains url path
    sublink = match.group(4).rstrip("/")
    # Extract host part from match object
    hostlink = match.group(3)
        
    # check if https works
    url = "https://" + hostlink + sublink
    if check_weblink(url): 
        lut[match.group(0)] = url
        return url          # If unmodified link works wirth https return url
    
    # check for http
    url = "http://" + hostlink + sublink
    if check_weblink(url):
        lut[match.group(0)] = url
        return url          # If unmodified link works wirth http return url
    
    # Set prefix of url
    if match.group(1) == "https://":
        prefix = "https://"
    # Check host part of url with https. If it does not work, schema (prefix) is http
    else:   
        url = "https://" + match.group(3)
        if check_weblink(url):
            prefix = "https://"
        else:
            prefix = "http://"
                
    # Modify url subpart (path) and check if link remains broken
    # Split path (sublink) by "/"
    n = len(sublink.lstrip('/').split('/'))
    for _ in range(n):
        # Removes last subpath of sublink (path)
        sublink = reg.sub('', sublink, 1)
        url = prefix + hostlink + sublink
        if check_weblink(url):
            lut[match.group(0)] = url
            return url
                
    # Link broken or other problem
    lut[match.group(0)] = False
    return ''
    
if __name__ == '__main__':
    # osm data files
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=20.osm'
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
    osm_file = '../data/GE_SH_PI_elmshorn_uetersen.osm'
    print("Identify weblinks by keyword:")
    weblinks, badlinks = weblinks_by_key(osm_file)

    print("\n")
    print("Show values of wikipedia keys (badlinks):")
    for i in range(10):
        print(badlinks['wikipedia'][i])

    print("\n")
    print("Show values of image keys (weblinks):")   
    for i in range(10):
        print(weblinks['image'][i])
    
    print("\n")
    print("Find further weblinks in other keys:")
    weblinks_val = weblinks_by_value(osm_file)
       
    # Additional keys to be checked for weblinks extracted from weblinks_val 
    additional_keys = ('openGeoDB:version', 'email', 'note:de', 'source', 'contact:email',
                         'name', 'contact:facebook', 'internet_access:ssid', 'note', 
                         'operator', 'network' )
    for key in additional_keys:
        print("\n")
        print(key + ":")
        for link in weblinks_val[key]:
            print(link)
    
    # Update wewblinks
    # Change to smaller OSM file for weblink checks and updates
    osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
    print("\n")
    print("Update weblinks:")
    #lut, stats = weblink.check_url(osm_file, output=True, JSON_out='weblink_lut.JSON')
    lut, stats = check_url(osm_file, output=True)
            
    