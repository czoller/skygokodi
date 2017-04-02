# -*- coding: utf-8 -*-
# Module: default
# Author: NaZo

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import urllib
import json

_HANDLE = int(sys.argv[1])
_SKYGO_MAIN_URL = 'http://www.skygo.sky.de';
_SKYGO_LIVEPLANER_URL = 'http://www.skygo.sky.de/sg/multiplatform/web/json/automatic_listing/sport/event/13.json';


class SkyGoVideo(object):
    
    def __init__(self, json):
        
        self.title = json['title'];
        self.thumb = json['main_picture']['picture'][3];
#        self.fanart = json['main_picture']['picture'][9];
        self.date = json['technical_event']['on_air']['start_date'].replace('/', '-');
        self.category = json['category']['main']['content'];
        self.page = json['webvod_canonical_url']
        
    def toListItem(self):
        listItem = xbmcgui.ListItem(label=self.title)
        listItem.setInfo('video', {'title': self.title, 'genre': self.category, 'date': self.date})
        listItem.setProperty('IsPlayable', 'true')
        thumb = _SKYGO_MAIN_URL + self.thumb['path'] + '/' + self.thumb['file'] 
        fanart = _SKYGO_MAIN_URL + self.fanart['path'] + '/' + self.fanart['file'] 
        listItem.setArt({'thumb': thumb, 'icon': thumb, 'fanart': fanart})
        page = self.page
        url = 'plugin://plugin.program.chrome.launcher/?url=' + page + '&mode=showSite&stopPlayback=no'
        
        return (url, listItem, False)
    
def toListItem(skygoObject):
    return skygoObject.toListItem()

def loadVideoList():
    
    file = urllib.urlopen(_SKYGO_LIVEPLANER_URL)
    results = json.load(file)
    
    listItems = []
    for item in results['listing']['listing']['asset']:
        listItems.append(SkyGoVideo(item))

    return listItems
    
def listVideos():
    
    listing = map(toListItem, loadVideoList())
    xbmcplugin.addDirectoryItems(_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(_HANDLE)


def showVideo(path):

    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def router(paramstring):

    params = dict(parse_qsl(paramstring))
    if params and params['show'] == 'play':
        showVideo(params['video'])
    else:
        listVideos()


if __name__ == '__main__':
    router(sys.argv[2][1:])
