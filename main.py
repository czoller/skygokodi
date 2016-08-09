# -*- coding: utf-8 -*-
# Module: default
# Author: NaZo

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import urllib
import json

_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
_WIN = xbmcgui.Window()
_WERDER_URL = 'http://www.werder.de'


class WerderVideo(object):
    
    def __init__(self, json):

        self.title = json['title'] 
        self.image = json['image'].lstrip('/')
        self.page = json['videoInformation']['detailPage']
        self.primaryTagLabel = json['videoInformation']['primaryTag']
        self.description = json['description']
        self.date = json['publishDateTime']
    
    def toListItem(self):
        listItem = xbmcgui.ListItem(label=self.title)
        listItem.setInfo('video', {'title': self.title, 'genre': self.primaryTagLabel, 'date': self.date, 'plot': self.description, 'plotoutline': self.description})
        listItem.setProperty('IsPlayable', 'true')
        thumb = _WERDER_URL + '/?eID=crop&width=400&height=300&file=' + self.image
        fanart = _WERDER_URL + '/?eID=crop&width=' + str(_WIN.getWidth()) + '&height=' + str(_WIN.getHeight()) + '&file=' + self.image
        listItem.setArt({'thumb': thumb, 'icon': thumb, 'fanart': fanart})
        page = _WERDER_URL + self.page
        url = 'plugin://plugin.program.chrome.launcher/?url=' + page + '&mode=showSite&stopPlayback=no'
        
        return (url, listItem, False)
    
    
class WerderGroup(object):
    
    def __init__(self, json):
        self.id = json['id']
        self.title = json['titleDe']
        #TODO tags
    
    def toListItem(self):
        listItem = xbmcgui.ListItem(label=self.title)
        listItem.setInfo('video', {'title': self.title})
        url = _URL + '?show=group&group=' + str(self.id)
        
        return (url, listItem, True)
    
    
def loadVideoList(tagId = 0, limit = 0):
    
    tagParam = 'tagList=' + str(tagId) if tagId > 0 else ''
    limitParam = 'limit=' + str(limit) if limit > 0 else ''
    
    url = _WERDER_URL + '/api/rest/video/list/compact?' + limitParam  + '&orderBy=publishDateTime&orderByDesc=true&page=1&strict=true' + tagParam
    file = urllib.urlopen(url)
    results = json.load(file)
    
    listItems = []
    for item in results['items']:
        listItems.append(WerderVideo(item).toListItem())

    return listItems
    
def loadGroupList():
    
    url = _WERDER_URL + '/api/rest/tag/group/list'
    file = urllib.urlopen(url)
    results = json.load(file)
    
    listItems = []
    for group in results:
        listItems.append(WerderGroup(group).toListItem())

    return listItems


def listLatestVideos():
    
    archiveItem = xbmcgui.ListItem(label='Archiv')
    archiveItem.setInfo('video', {'title': 'Archiv'})
    archiveUrl = _URL + '?show=archive'
    
    listing = [(archiveUrl, archiveItem, True)] + loadVideoList(0, 20)
    xbmcplugin.addDirectoryItems(_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(_HANDLE)


def listGroups():
    
    listing = loadGroupList()
    xbmcplugin.addDirectoryItems(_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(_HANDLE)


def showVideo(path):

    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    params = dict(parse_qsl(paramstring))
    if params:
        if params['show'] == 'latest':
            listLatestVideos()
        elif params['show'] == 'archive':
            listGroups()
#         elif params['show'] == 'group':
#             listTags(params['tag'])
#         elif params['show'] == 'tag':
#             listVideos(params['tag'])
        elif params['show'] == 'play':
            showVideo(params['video'])
    else:
        listLatestVideos()



if __name__ == '__main__':
    router(sys.argv[2][1:])
