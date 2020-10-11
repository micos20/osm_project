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
    webkeys     = ['website', 'url', 'image', 'removed:website', 'contact:website', 
                   'source', 'contact:facebook', 'internet_access:ssid', 'note']
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')
    
    weblink_LUT = {}
    stats = defaultdict(list)
    
    # Parsing the file
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in webkeys:
            match = regex_weblink.match(tag.get('v'))           
            if match != None:
                url = match.group(0)
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
                else:
                    new_url = update_webkey(match, weblink_LUT)

    # Output
    if output == True:
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
                
        # print stats
        print("Nbr insecure urls:  old/{:>4d}   new/{:>4d}".format(len(stats['old insecure links']), len(stats['new insecure links'])))
        print("Nbr secure urls:    old/{:>4d}   new/{:>4d}".format(len(stats['old secure links']), len(stats['new secure links'])))
        print("Nbr missing schemes: {:>4d}".format(len(stats['old undef links'])))
        print("Nbr modified links:  {:>4d}".format(len(stats['modified links'])))
        print("Nbr broken links:    {:>4d}".format(len(stats['broken links'])))
        print("Ndr of doublicates:  {:>4d}".format(len(stats['doublicate'])))
            
    if JSON_out != False:
        if not write_JSON(weblink_LUT, JSON_out):
            print("JSON output went wrong!")
        else:
            print("JSON output successful!")
        
    return weblink_LUT, stats
        
        
def update_webkey(match, lut={}):                  
    reg = re.compile(r'/[^/]*$')            
    
    sublink = match.group(4).rstrip("/")
    hostlink = match.group(3)
        
    # check if https works
    url = "https://" + hostlink + sublink
    if check_weblink(url): 
        lut[match.group(0)] = url
        return url
    
    # check for http
    url = "http://" + hostlink + sublink
    if check_weblink(url):
        lut[match.group(0)] = url
        return url        
    
    # Set prfix of url
    if match.group(1) == "https://":
        prefix = "https://"
    else:   
        url = "https://" + match.group(3)
        if check_weblink(url):
            prefix = "https://"
        else:
            prefix = "http://"
                
    # Modify url subpart and check if link remains broken
    n = len(sublink.lstrip('/').split('/'))
    for _ in range(n):
        sublink = reg.sub('', sublink, 1)
        url = prefix + hostlink + sublink
        if check_weblink(url):
            lut[match.group(0)] = url
            return url
                
    # Link broken or other problem
    lut[match.group(0)] = False
    return ''
    
if __name__ == '__main__':
    weblinks, badlinks = weblinks_by_key(osm_file)
    
    for i in range(10):
        print(badlinks['wikipedia'][i])
    
    for i in range(10):
        print(weblinks['image'][i])
    
    

