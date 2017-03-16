import uuid
import hmac
import hashlib
import string, random
from StringIO import StringIO
import gzip
from urllib2 import URLError, HTTPError
import sys
import xbmc,xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
import urllib, urllib2, httplib2
import json
import HTMLParser
import calendar
from datetime import datetime, timedelta
import time
import cookielib
import base64


addon_handle = int(sys.argv[1])
SCORE_COLOR = 'FF00B7EB'
UPCOMING = 'FFD2D2D2'
CRITICAL ='FFD10D0D'
FINAL = 'FF666666'
FREE = 'FF43CD80'
GAMETIME_COLOR = 'FFFFFF66'
BASE_PATH = 'https://data.ncaa.com/mml/2017/mobile'

def colorString(string, color):
    return '[COLOR='+color+']'+string+'[/COLOR]'

def stringToDate(string, date_format):
    try:
        date = datetime.strptime(str(string), date_format)
    except TypeError:
        date = datetime(*(time.strptime(str(string), date_format)[0:6]))                

    return date

def FIND(source,start_str,end_str):    
    start = source.find(start_str)
    end = source.find(end_str,start+len(start_str))

    if start != -1:        
        return source[start+len(start_str):end]
    else:
        return ''

def GET_RESOURCE_ID():
    #########################
    # Get resource_id
    #########################
    """
    GET http://stream.nbcsports.com/data/mobile/passnbc.xml HTTP/1.1
    Host: stream.nbcsports.com
    Connection: keep-alive
    Accept: */*
    User-Agent: NBCSports/1030 CFNetwork/711.3.18 Darwin/14.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connect
    """
    #req = urllib2.Request(ROOT_URL+'passnbc.xml')  
    #req.add_header('User-Agent',  UA_MMOD)
    #response = urllib2.urlopen(req)        
    #resource_id = response.read()
    #response.close() 
    #resource_id = resource_id.replace('\n', ' ').replace('\r', '')
    #resource_id = '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel><title>nbcsports</title><item><title>NBC Sports PGA Event</title><guid>123456789</guid><media:rating scheme="urn:vchip">TV-PG</media:rating></item></channel></rss>'
    resource_id='truTV&resource_id=TNT&resource_id=TBS&authentication_token=%3CsignatureInfo%3ERnNoE2akRWIggEQRFpt3J68BjpOwHdz8h7MHXMrbvaO3YCPcxqQaEO0v6IVkd5YXX3o2GQx1jodloBN3d07EnW7gJPiqH5WnNQWw4JzRdryvvmU1og1myAKWJeAmlWVQwWbh%2F%2BIvYg0o4ixiH2FXV0f4aabonzveA7u1QZ5e1BE%3D%3CsignatureInfo%3E%3CsimpleAuthenticationToken%3E%3CsimpleTokenAuthenticationGuid%3Eca0aa85164c3f2e3e90ea8559e93ae07%3C%2FsimpleTokenAuthenticationGuid%3E%3CsimpleSamlSessionIndex%3E0XEThQfyW5yOFn5%2B4GBReoziz8aNdYNDBqG6%2FDUJTLJJRN5LGMKmvDf1Sbp1YXts%3C%2FsimpleSamlSessionIndex%3E%3CsimpleTokenRequestorID%3EMML%3C%2FsimpleTokenRequestorID%3E%3CsimpleTokenDomainName%3Eadobe.com%3C%2FsimpleTokenDomainName%3E%3CsimpleTokenExpires%3E2016%2F07%2F15%2005%3A10%3A34%20GMT%20-0700%3C%2FsimpleTokenExpires%3E%3CsimpleTokenMsoID%3ETempPass%3C%2FsimpleTokenMsoID%3E%3CsimpleTokenDeviceID%3E%3CsimpleTokenFingerprint%3E5c15e4c07ddbbf09276fcfc54489a6e9ededb0b6%3C%2FsimpleTokenFingerprint%3E%3C%2FsimpleTokenDeviceID%3E%3CsimpleSamlNameID%3E0XEThQfyW5yOFn5%2B4GBReoziz8aNdYNDBqG6%2FDUJTLJJRN5LGMKmvDf1Sbp1YXts%3C%2FsimpleSamlNameID%3E%3C%2FsimpleAuthenticationToken%3E&requestor_id=MML'
    return resource_id



def SET_STREAM_QUALITY(url):
    
    stream_url = {}
    stream_title = []

    #Open master file a get cookie(s)
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [ ("Accept", "*/*"),
                        ("Accept-Encoding", "deflate"),
                        ("Accept-Language", "en-us"),                                                                                                              
                        ("User-Agent", UA_MMOD)]

    resp = opener.open(url)
    master = resp.read()
    resp.close()  

    cookies = '' 
    for cookie in cj:                    
        if cookies != '':
            cookies = cookies + "; "
        cookies = cookies + cookie.name + "=" + cookie.value
    
    line = re.compile("(.+?)\n").findall(master)  
    
    xplayback = ''.join([random.choice('0123456789ABCDEF') for x in range(32)])
    xplayback = xplayback[0:7]+'-'+xplayback[8:12]+'-'+xplayback[13:17]+'-'+xplayback[18:22]+'-'+xplayback[23:]

    for temp_url in line:
        if '#EXT' not in temp_url:
            temp_url = temp_url.rstrip()
            start = 0
            if 'http' not in temp_url:
                if 'master' in url:
                    start = url.find('master')
                elif 'manifest' in url:
                    start = url.find('manifest')                
            
            if url.find('?') != -1:
                replace_url_chunk = url[start:url.find('?')]    
            else:
                replace_url_chunk = url[start:]    
            
            
            temp_url = url.replace(replace_url_chunk,temp_url)              
            temp_url = temp_url.rstrip() + "|User-Agent=" + UA_MMOD
            
            #if cookies != '':                
            #temp_url = temp_url + "&Cookie=" + cookies
            
            stream_title.append(desc)
            stream_url.update({desc:temp_url})
        else:
            desc = ''
            start = temp_url.find('BANDWIDTH=')
            if start > 0:
                start = start + len('BANDWIDTH=')
                end = temp_url.find(',',start)
                desc = temp_url[start:end]
                try:
                    int(desc)
                    desc = str(int(desc)/1000) + ' kbps'
                except:
                    pass            
    
    
    if len(stream_title) > 0:
        ret =-1      
        stream_title.sort(key=natural_sort_key)  
        print "PLAY BEST SETTING"
        print PLAY_BEST
        if str(PLAY_BEST) == 'true':
            ret = len(stream_title)-1            
        else:
            dialog = xbmcgui.Dialog() 
            ret = dialog.select('Choose Stream Quality', stream_title)
            print ret
        if ret >=0:
            url = stream_url.get(stream_title[ret])           
        else:
            sys.exit()
    else:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Streams Not Found', msg)


    return url


def natural_sort_key(s):
    _nsre = re.compile('([0-9]+)')
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)] 


def SAVE_COOKIE(cj):
    # Cookielib patch for Year 2038 problem
    # Possibly wrap this in if to check if device is using a 32bit OS
    for cookie in cj:
        # Jan, 1 2038
        if cookie.expires >= 2145916800:
            #Jan, 1 2037
            cookie.expires =  2114380800
    
    cj.save(ignore_discard=True);  




def getTournamentInfo():
    now = datetime.now()
    url = 'http://data.ncaa.com/mml/'+str(now.year)+'/mobile/tournament.json'
    req = urllib2.Request(url)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
    req.add_header('Connection', 'keep-alive')
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_MMOD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)    
    json_source = json.load(response)                           
    response.close() 

    teams = json.dumps(json_source['tournament']['teams']['team'])

    return teams

def getTeamInfo(teams, team_id):    
    all_teams = json.loads(teams)
    team_name = ''
    link_name = ''
    
    for team in all_teams:        
        if str(team['id']) == str(team_id):
            team_name = team['school']
            link_name = team['link']
            break

    return team_name, link_name

def getCurrentInfo():
    now = datetime.now()
    url = 'http://data.ncaa.com/mml/'+str(now.year)+'/mobile/current.json'
    req = urllib2.Request(url)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
    req.add_header('Connection', 'keep-alive')
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_MMOD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)    
    json_source = json.load(response)                           
    response.close() 

    current_games = ''
    
    try:
        current_games = json.dumps(json_source['current']['game'])
    except:
        pass

    return current_games


def getGameClock(current_games, game_id):
    '''
    {
        "alert": "1",
        "cardInc": "93",
        "clock": "1:43",
        "gameInc": "1458243199",
        "id": "202",
        "pbpInc": "1458243199",
        "per": "2",
        "ptsH": "59",
        "ptsV": "66",
        "state": "3",
        "rpyV": false,
        "radio": true,
        "rcpV": false,
        "preV": true,
        "video": true
      }
    '''
    games = json.loads(current_games)
    clock = 'End'
    ordinal_indicator = ''

    for game in games:        
        if str(game['id']) == str(game_id):
            print game
            clock = str(game['clock'])
            per = str(game['per'])
            if per != '':
                if int(per) == 1:
                    ordinal_indicator = "st"
                elif int(per) == 2:
                    ordinal_indicator = "nd"
                elif int(per) == 3:
                    ordinal_indicator = "rd"
                else:
                    ordinal_indicator = "th"                
            break

    return clock + ' ' + per + ordinal_indicator
    

def getAppConfig():
    #https://data.ncaa.com/mml/2017/mobile/appConfig_iPhone.json    
    now = datetime.now()
    url = 'https://data.ncaa.com/mml/'+str(now.year)+'/mobile/appConfig_iPhone.json'
    req = urllib2.Request(url)    
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_IPHONE)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  
    
    api = json_source['api']    
    #BASE_PATH = api['base']['sche']



def tokenTurner(media_token, stream_url, mvpd):
        #stream_url
        #http://mml01-i.akamaihd.net/hls/live/265830/201/villanovavsmt-st-marys/connected1/master.m3u8
        '''
        POST http://token.vgtf.net/token/token_spe_mml?profile=mml HTTP/1.1
        Current-Type: application/x-www-form-urlencoded
        Content-Length: 719
        Content-Type: application/x-www-form-urlencoded
        Host: token.vgtf.net
        Connection: Keep-Alive
        Pragma: no-cache

        &accessTokenType=Adobe
        &accessToken=%3CsignatureInfo%3EXv1rtBY0MP5%2FCkaobJcjdkz0%2Ff3gZ9248XqG7hULT5qWA0UZP04AY2efA21VBxBR5r1IWZMNx5doAPmYk9SKnaKdN45T88BdoOO8aeQeet2sEDXSHu%2BqjBLLYcW6%2BqNcxU3TT1KzQkqv90vIq6BdlqDEHbI5p%2FpwwWVX9hAB9%2BM%3D%3CsignatureInfo%3E%3CauthToken%3E%3CsessionGUID%3Ea6c1d2fa9725d7857b6a9d3aa9195040%3C%2FsessionGUID%3E%3CrequestorID%3EMML%3C%2FrequestorID%3E%3CresourceID%3EtruTV%3C%2FresourceID%3E%3Cttl%3E420000%3C%2Fttl%3E%3CissueTime%3E2017-03-15+16%3A40%3A46+-0700%3C%2FissueTime%3E%3CmvpdId%3ETWC%3C%2FmvpdId%3E%3C%2FauthToken%3E
        &sessionId=05a564d7c8622b5dd1c67f0ae737c5bb1515d66a~auth~win8~mml~100~1489621236122
        &mvpd=TWC
        &throttled=no
        &path=/hls/live/265823-b/103/uc-davisvsnc-central/de/*
        '''
        url = 'http://token.vgtf.net/token/turner'
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Current-Type", "application/x-www-form-urlencoded"),                            
                            ("Pragma", "no-cache"),
                            ("Content-Type", "application/x-www-form-urlencoded"),                            
                            ("Connection", "keep-alive"),                                                                            
                            ("User-Agent", UA_MMOD)]
        
        xbmc.log(str(base64.b64decode(media_token)))
        #<signatureInfo>bfT/fz+B4Yx6GjlJ+eS2KHU9xxagNVSO48EqABBTY9/yWI6DFj9wUaZjrmWpjFaB2j1zlM86A666+7YTHlNZ2ilHvi23iZEs6IQ8Jr2jEGgx/tGJ+8XqSl+UHlbG2JLUFw3i4IFBpGaD/FwPXQSIdXuSayrHZ6WDWnwTl2ini2A=<signatureInfo><authToken><sessionGUID>a6c1d2fa9725d7857b6a9d3aa9195040</sessionGUID><requestorID>MML</requestorID><resourceID>truTV</resourceID><ttl>420000</ttl><issueTime>2017-03-16 07:39:48 -0700</issueTime><mvpdId>TWC</mvpdId></authToken>
        payload = urllib.urlencode({'accessToken' : str(base64.b64decode(media_token)),                                
                                'accessTokenType' : 'Adobe',
                                #'sessionId': '05a564d7c8622b5dd1c67f0ae737c5bb1515d66a~auth~win8~mml~100~1489621236122',
                                'throttled' : 'no',
                                'mvpd' : mvpd,
                                #'path': '/hls/live/265823-b/103/uc-davisvsnc-central/de/*'
                                'path' : FIND(stream_url,BASE_PATH,'master.m3u8')+'*'
                                })

        resp = opener.open(url, payload)
        response = resp.read()
        #<token>PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+PGF1dGhUb2tlbj48cmVzb3VyY2VJRD5UTlQ8L3Jlc291cmNlSUQ+PHRpdGxlSUQvPjxyZXF1ZXN0b3JJRD50dXJuZXI8L3JlcXVlc3RvcklEPjxpc3N1ZVRpbWU+MjAxNi0wMy0xOFQwMDowODo0MSswMDAwPC9pc3N1ZVRpbWU+PHR0bD4zMDAwMDA8L3R0bD48b3BhcXVlVXNlcklEPmE2YzFkMmZhOTcyNWQ3ODU3YjZhOWQzYWE5MTk1MDQwPC9vcGFxdWVVc2VySUQ+PFNpZ25hdHVyZSB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PFNpZ25lZEluZm8+PENhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy14bWwtYzE0bi0yMDAxMDMxNSIvPjxTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjcnNhLXNoYTEiLz48UmVmZXJlbmNlIFVSST0iIj48VHJhbnNmb3Jtcz48VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz48L1RyYW5zZm9ybXM+PERpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNzaGExIi8+PERpZ2VzdFZhbHVlPldYZXoxcWFLR2RKcVFhUHZwZ1NlQ3phRFBWOD08L0RpZ2VzdFZhbHVlPjwvUmVmZXJlbmNlPjwvU2lnbmVkSW5mbz48U2lnbmF0dXJlVmFsdWU+SFpzOW5wOWptTVFGNFUrclNuejFpanJCYjBOQ21qYXc0em9IdVcwek1jeC9FdkJSRnpVSlZCaExDMWNKYlY2SU5ZZUNZVno5Wnhhbwp5THhTM2s3Q04wVE13ZjRVSXl6UG04N2gwbWxndVV0R0RCOXhiZStmeDFzdTFCNnFBUmMyYW1lakNOUlpyV0tNTGVOODhLeWR1eVdQCnE3R1Q0YXpZaVI0dG5jN0VyL3M9PC9TaWduYXR1cmVWYWx1ZT48L1NpZ25hdHVyZT48L2F1dGhUb2tlbj4=</token>
        resp.close()    
        hdnts = FIND(response,'<token>','</token>')  
        #http://mml03-i.akamaihd.net/hls/live/265823-b/103/uc-davisvsnc-central/de/master.m3u8?hdnts=exp=1489621546~acl=/hls/live/265823-b/103/*~hmac=072322367151db0fcc56acef76df509090fab91a999add08872c3d65fe1d9f1b 
        #stream_url += '?hdnts='+hdnts
        xbmc.log(stream_url)
        #mediaAuth = getAuthCookie()
        stream_url = stream_url + '|User-Agent='+UA_MMOD
        #+'&Cookie='+mediaAuth
        

        return stream_url


def fetchStream(game_id):
    ''' 
        http://data.ncaa.com/mml/2017/mobile/video/103_bk.json
    GET http://data.ncaa.com/mml/2016/mobile/video/201.json HTTP/1.1
    Host: data.ncaa.com
    Connection: keep-alive
    Accept: */*
    User-Agent: MML/43 CFNetwork/758.2.8 Darwin/15.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: keep-alive

    {
        "updatedTimestamp": 
        "2017-3-14 23:52:07 AST",
        "mobile": 
        "http://mml01-i.akamaihd.net/hls/live/265801/101/wake-forestvskansas-st/mo/master.m3u8",
        "desktop": 
        "http://mml01-i.akamaihd.net/hls/live/265801/101/wake-forestvskansas-st/de/master.m3u8",
        "connected1": 
        "http://mml01-i.akamaihd.net/hls/live/265801/101/wake-forestvskansas-st/connected1/master.m3u8",
        "connected2":
        "http://mml01-i.akamaihd.net/hls/live/265801/101/wake-forestvskansas-st/connected2/master.m3u8"
        }


    Recap
    http://data.ncaa.com/mml/2017/mobile/game/game_101.json 
    '''
    now = datetime.now()
    req = urllib2.Request('http://data.ncaa.com/mml/'+str(now.year)+'/mobile/video/'+game_id+'_bk.json')    
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_MMOD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  
    
    stream_url = json_source['connected1']
    
    
    
    return stream_url


def getAuthCookie():
    mediaAuth = ''    
    try:
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)    

        #If authorization cookie is missing or stale, perform login    
        for cookie in cj:            
            if cookie.name == "mediaAuth" and not cookie.is_expired():            
                mediaAuth = 'mediaAuth='+cookie.value 
    except:
        pass

    return mediaAuth


def addStream(name,link_url,title,game_id,icon=None,fanart=None):
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(link_url)+"&mode="+str(104)+"&name="+urllib.quote_plus(name)+"&game_id="+urllib.quote_plus(str(game_id))    
    
    liz=xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=ICON)     
    
    if fanart != None:
        liz.setProperty('fanart_image', fanart)       
    else:
        liz.setProperty('fanart_image', FANART)

    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )    

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, 'episodes')    
    return ok

def addDir(name,url,mode,iconimage,fanart=None):       
    ok=True    
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    
    if iconimage != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 

    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)


    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    return ok


def addLink(name,url,iconimage,fanart=None):
    ok=True            
    if iconimage != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 

    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty("IsPlayable", "true")

    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)


    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)    
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    return ok


# KODI ADDON GLOBALS
ADDON_HANDLE = int(sys.argv[1])
ROOTDIR = xbmcaddon.Addon(id='plugin.video.mmlive').getAddonInfo('path')
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
KODI_VERSION = float(re.findall(r'\d{2}\.\d{1}', xbmc.getInfoLabel("System.BuildVersion"))[0])
LOCAL_STRING = ADDON.getLocalizedString
FANART = ROOTDIR+"/fanart.jpg"
ICON = ROOTDIR+"/icon.png"

#Settings file location
settings = xbmcaddon.Addon(id='plugin.video.mmlive')

#Main settings
NO_SPOILERS = str(settings.getSetting(id="no_spoilers"))

#User Agents
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143'
UA_PC = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
UA_ADOBE_PASS = 'AdobePassNativeClient/1.9.4 (iPhone; U; CPU iPhone OS 9.2.1 like Mac OS X; en-us)'
UA_MMOD = 'MML/43 CFNetwork/758.2.8 Darwin/15.0.0'



#Create Random Device ID and save it to a file
fname = os.path.join(ADDON_PATH_PROFILE, 'device.id')
if not os.path.isfile(fname):
    if not os.path.exists(ADDON_PATH_PROFILE):
        os.makedirs(ADDON_PATH_PROFILE)
    new_device_id = ''.join([random.choice('0123456789abcdef') for x in range(64)])
    device_file = open(fname,'w')   
    device_file.write(new_device_id)
    device_file.close()

fname = os.path.join(ADDON_PATH_PROFILE, 'device.id')
device_file = open(fname,'r') 
DEVICE_ID = device_file.readline()
device_file.close()


#Event Colors
FREE = 'FF43CD80'
LIVE = 'FF00B7EB'
UPCOMING = 'FFFFB266'
FREE_UPCOMING = 'FFCC66FF'