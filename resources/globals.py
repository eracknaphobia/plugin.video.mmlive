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

def GET_SIGNED_REQUESTOR_ID():

    ##################################################
    # Use this call to get Adobe's Signed ID
    ##################################################
    """
    GET http://stream.nbcsports.com/data/mobile/configuration-2014-RSN-Sections.json HTTP/1.1
    Host: stream.nbcsports.com
    Connection: keep-alive
    Accept: */*
    User-Agent: NBCSports/1030 CFNetwork/711.3.18 Darwin/14.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    """
    req = urllib2.Request(ROOT_URL+'configuration-2014-RSN-Sections.json')  
    req.add_header('User-Agent',  UA_MMOD)
    response = urllib2.urlopen(req)        

    json_source = json.load(response)                       
    response.close() 

    print "ADOBE PASS"
    signed_requestor_id = json_source['adobePassSignedRequestorId']
    signed_requestor_id = signed_requestor_id.replace('\n',"")
    print signed_requestor_id
    
    return signed_requestor_id

def SET_STREAM_QUALITY(url):
    print url
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
    
    print master
    print cookies
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

    '''
    url = url.replace('master.m3u8',q_lvl_golf+'/proge.m3u8')       
    url = url.replace('manifest(format=m3u8-aapl-v3)','QualityLevels('+q_lvl+')/Manifest(video,format=m3u8-aapl-v3,audiotrack=audio_en_0)')       
    url = url.replace('manifest(format=m3u8-aapl,filtername=vodcut)','QualityLevels('+q_lvl+')/Manifest(video,format=m3u8-aapl,filtername=vodcut)')
    url = url.replace('manifest(format=m3u8-aapl-v3,filtername=vodcut)','QualityLevels('+q_lvl+')/Manifest(video,format=m3u8-aapl-v3,audiotrack=audio_en_0,filtername=vodcut)')
    '''
    
    print "STREAM URL === " + url 

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


def CLEAR_SAVED_DATA():
    print "IN CLEAR"
    try:
        os.remove(ADDON_PATH_PROFILE+'/device.id')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/provider.info')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/cookies.lwp')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/auth.token')
    except:
        pass
    ADDON.setSetting(id='clear_data', value='false')   


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
    


def tokenTurner(media_token):
        '''
        POST http://token.vgtf.net/token/turner HTTP/1.1
        Host: token.vgtf.net
        Content-Type: application/x-www-form-urlencoded
        Connection: keep-alive
        Current-Type: application/x-www-form-urlencoded
        Connection: keep-alive
        Accept: */*
        Accept-Language: en-us
        Content-Length: 666
        Accept-Encoding: gzip, deflate
        User-Agent: MML/43 CFNetwork/758.2.8 Darwin/15.0.0

        accessToken=%3CsignatureInfo%3EWxrCt58xTmqQh2DwO0NqNNi%2BZdBjVXx3GQjyXQKIJ%2BVezCXviDbtugc2nCOicm5rnKZSvBTNOrGfn2ZrcNNsAaGdIBSFbo%2FEpboV6CofjuvO5Sm1APd3ispvH07GfmOhVBvmdDz0gOQ22MjVBz9qGRbFPhks%2FPpMddjV0Zuufds%3D%3CsignatureInfo%3E%3CauthToken%3E%3CsessionGUID%3E613e99bf2db476308f802091f8462819%3C%2FsessionGUID%3E%3CrequestorID%3EMML%3C%2FrequestorID%3E%3CresourceID%3ETNT%3C%2FresourceID%3E%3Cttl%3E420000%3C%2Fttl%3E%3CissueTime%3E2016-03-17%2015%3A01%3A31%20-0700%3C%2FissueTime%3E%3CmvpdId%3ETempPass%3C%2FmvpdId%3E%3C%2FauthToken%3E
        &appData={'clientTime':10800,'serverTime':10800,'unrecordedTime':0}
        &timeRemaining=10800
        &sessionId=
        &mvpd=TempPass
        &throttled=yes
        '''
        url = 'http://token.vgtf.net/token/turner'
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),                            
                            ("Connection", "keep-alive"),                                                                            
                            ("User-Agent", UA_MMOD)]
        

        data = urllib.urlencode({'accessToken' : media_token})

        resp = opener.open(url, data)
        response = resp.read()
        #<token>PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+PGF1dGhUb2tlbj48cmVzb3VyY2VJRD5UTlQ8L3Jlc291cmNlSUQ+PHRpdGxlSUQvPjxyZXF1ZXN0b3JJRD50dXJuZXI8L3JlcXVlc3RvcklEPjxpc3N1ZVRpbWU+MjAxNi0wMy0xOFQwMDowODo0MSswMDAwPC9pc3N1ZVRpbWU+PHR0bD4zMDAwMDA8L3R0bD48b3BhcXVlVXNlcklEPmE2YzFkMmZhOTcyNWQ3ODU3YjZhOWQzYWE5MTk1MDQwPC9vcGFxdWVVc2VySUQ+PFNpZ25hdHVyZSB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PFNpZ25lZEluZm8+PENhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy14bWwtYzE0bi0yMDAxMDMxNSIvPjxTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjcnNhLXNoYTEiLz48UmVmZXJlbmNlIFVSST0iIj48VHJhbnNmb3Jtcz48VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz48L1RyYW5zZm9ybXM+PERpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNzaGExIi8+PERpZ2VzdFZhbHVlPldYZXoxcWFLR2RKcVFhUHZwZ1NlQ3phRFBWOD08L0RpZ2VzdFZhbHVlPjwvUmVmZXJlbmNlPjwvU2lnbmVkSW5mbz48U2lnbmF0dXJlVmFsdWU+SFpzOW5wOWptTVFGNFUrclNuejFpanJCYjBOQ21qYXc0em9IdVcwek1jeC9FdkJSRnpVSlZCaExDMWNKYlY2SU5ZZUNZVno5Wnhhbwp5THhTM2s3Q04wVE13ZjRVSXl6UG04N2gwbWxndVV0R0RCOXhiZStmeDFzdTFCNnFBUmMyYW1lakNOUlpyV0tNTGVOODhLeWR1eVdQCnE3R1Q0YXpZaVI0dG5jN0VyL3M9PC9TaWduYXR1cmVWYWx1ZT48L1NpZ25hdHVyZT48L2F1dGhUb2tlbj4=</token>
        resp.close()    
        partnerParam1 = FIND(response,'<token>','</token>')  
        print "param 1"
        print partnerParam1

        return partnerParam1


def fetchStream(game_id, partnerParam1):
    ''' 
    GET http://data.ncaa.com/mml/2016/mobile/video/201.json HTTP/1.1
    Host: data.ncaa.com
    Connection: keep-alive
    Accept: */*
    User-Agent: MML/43 CFNetwork/758.2.8 Darwin/15.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: keep-alive

    Recap
    http://data.ncaa.com/mml/2017/mobile/game/game_101.json 
    '''
    now = datetime.now()
    req = urllib2.Request('http://data.ncaa.com/mml/'+str(now.year)+'/mobile/video/'+game_id+'.json')    
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_MMOD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  

    contentId = json_source['contentId']

    '''
    GET https://mm-ws.mms.ncaa.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3
    ?partnerParam1=PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8%2BPGF1dGhUb2tlbj48cmVzb3VyY2VJRD5UTlQ8L3Jlc291cmNlSUQ%2BPHRpdGxlSUQvPjxyZXF1ZXN0b3JJRD50dXJuZXI8L3JlcXVlc3RvcklEPjxpc3N1ZVRpbWU%2BMjAxNi0wMy0xN1QyMjowMTozMSswMDAwPC9pc3N1ZVRpbWU%2BPHR0bD4zMDAwMDA8L3R0bD48b3BhcXVlVXNlcklEPjYxM2U5OWJmMmRiNDc2MzA4ZjgwMjA5MWY4NDYyODE5PC9vcGFxdWVVc2VySUQ%2BPFNpZ25hdHVyZSB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI%2BPFNpZ25lZEluZm8%2BPENhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy14bWwtYzE0bi0yMDAxMDMxNSIvPjxTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjcnNhLXNoYTEiLz48UmVmZXJlbmNlIFVSST0iIj48VHJhbnNmb3Jtcz48VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz48L1RyYW5zZm9ybXM%2BPERpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNzaGExIi8%2BPERpZ2VzdFZhbHVlPld3Qi9jeXJCWklib1ZkVjZFRy9rMUxoN2VwMD08L0RpZ2VzdFZhbHVlPjwvUmVmZXJlbmNlPjwvU2lnbmVkSW5mbz48U2lnbmF0dXJlVmFsdWU%2BWDRKZmRyYXdVTGlPekZycjFRTFlmU2RmOXIrdFI5OEdoYkFXQW82bGVvZ2xoRCtCRWpyUVlzS0tVcGhJSUFOT0VHMnVERElwZEV6MgpyTXNjSjR4QUpTWE9VbnM2REJncnQxRWVnZGs5U2h2aTRLbzEwMC9lenFvaDY2Z1VuUWtPM0c1L0F1a29hTElqVFY1bUU4SVJ2cXhzClVkend0R3hvSnhPeHJ5Z29sY2M9PC9TaWduYXR1cmVWYWx1ZT48L1NpZ25hdHVyZT48L2F1dGhUb2tlbj4%3D
    &platform=IPHONE
    &playbackScenario=HTTP_CLOUD_IOS_TURNER
    &deviceId=6CF3EA47-BBE9-4C5B-A540-B7A3EB940589
    &subject=TURNER_MMOD_LIVE_VIDEO
    &auth=cookie
    &contentId=555183683 HTTP/1.1

    Host: mm-ws.mms.ncaa.com
    Accept: */*
    Proxy-Connection: keep-alive
    Cookie: mediaAuth=8e47612a02440b7ea81b2c96da980d1ee258b0e719c6f5538df7b7679a630b705d5c960a221749ee8a6fa90e25164223649362b5277199b99e49a2d2b0921a0f84a7cbf1eac8a09d675c7bf99db0e9cfdb0d1110929c333327d11e62e322b4c6f7df35ec32d1500b01be99b4469e296b28f998ab97dc40fe124b27649ec5740cee167a80d81e927e46dc4cbc1391a7d4c7d59007e8b07136c44f4a96e5e4ac2c8d946206c607c0836da7f38d0bb838f009bce22c4194f89678026f23bff87d4fd1cb73daba06d0c1
    User-Agent: MML/43 CFNetwork/758.2.8 Darwin/15.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    '''
    url = 'https://mm-ws.mms.ncaa.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3'
    url = url + '?partnerParam1='+urllib.quote_plus(partnerParam1)
    url = url + '&platform=IPHONE'
    url = url + '&playbackScenario=HTTP_CLOUD_IOS_TURNER'
    url = url + '&deviceId='+DEVICE_ID
    url = url + '&subject=TURNER_MMOD_LIVE_VIDEO'
    url = url + '&auth=cookie'
    url = url + '&contentId='+contentId
    url = url + '&format=json'
    
    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)         
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)       
    opener.addheaders = [ ("Accept", "*/*"),
                        ("Accept-Encoding", "deflate"),
                        ("Accept-Language", "en-us"),
                        ("Content-Type", "application/x-www-form-urlencoded"),                            
                        ("Connection", "keep-alive"),                                                                            
                        ("User-Agent", UA_MMOD)]


    
    #req.add_header("Accept", "*/*")
    #req.add_header("Accept-Encoding", "deflate")
    #req.add_header("Accept-Language", "en-US,en;q=0.8")                       
    #req.add_header("Connection", "keep-alive")
    #req.add_header("Authorization", authorization)
    #req.add_header("User-Agent", UA_NHL)
    #req.add_header("Proxy-Connection", "keep-alive")
    

    response = opener.open(req)
    json_source = json.load(response)       
    response.close()  
    #<![CDATA[http://ios.turner.ncaa.com/ls04/turner/2016/03/17/MMOD_VIDEO_MMOD_FLAGSvUNC_217_20160317/master_airplay.m3u8]]>
    print '---------------------------------------------------------------------------'
    print json_source
    print '---------------------------------------------------------------------------'
    stream_url = json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['url']
    print "stream url"
    print stream_url

    SAVE_COOKIE(cj)
    
    mediaAuth = getAuthCookie()
    stream_url = stream_url + '|User-Agent='+UA_MMOD+'&Cookie='+mediaAuth
    print stream_url

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
#QUALITY = int(settings.getSetting(id="quality"))
#USER_AGENT = str(settings.getSetting(id="user-agent"))
#CDN = int(settings.getSetting(id="cdn"))
USERNAME = str(settings.getSetting(id="username"))
PASSWORD = str(settings.getSetting(id="password"))
PROVIDER = str(settings.getSetting(id="provider"))
CLEAR = str(settings.getSetting(id="clear_data"))
#FREE_ONLY = str(settings.getSetting(id="free_only"))
#PLAY_MAIN = str(settings.getSetting(id="play_main"))
#PLAY_BEST = str(settings.getSetting(id="play_best"))
NO_SPOILERS = str(settings.getSetting(id="no_spoilers"))

if CLEAR == 'true':
   CLEAR_SAVED_DATA()

print 'PROVIDER!!!'
print PROVIDER
MSO_ID = ''
if PROVIDER == 'Cable One':
    MSO_ID = 'auth_cableone_net'
elif PROVIDER == 'Charter':    
    MSO_ID = 'Charter_Direct'  
elif PROVIDER == 'Comcast (xfinity)':    
    MSO_ID = 'Comcast_SSO'  
elif PROVIDER == 'Cox':
    MSO_ID = 'Cox' 
elif PROVIDER == 'Dish Network':
    MSO_ID = 'Dish' 
elif PROVIDER == 'Direct TV':
    MSO_ID = 'DTV'    
elif PROVIDER == 'Optimum':
    MSO_ID = 'Cablevision'
elif PROVIDER == 'Time Warner Cable':
    MSO_ID = 'TWC'
elif PROVIDER == 'Verizon':
    MSO_ID = 'Verizon'
elif PROVIDER == 'Bright House':
    MSO_ID = 'Brighthouse'


IDP_URL = 'https://sp.auth.adobe.com/adobe-services/1.0/authenticate/saml?domain_name=adobe.com&noflash=true&mso_id='+MSO_ID+'&requestor_id=MML&no_iframe=true&client_type=iOS&client_version=1.9.4&redirect_url=http://adobepass.ios.app/'           
ORIGIN = ''
REFERER = ''


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

#Create a file for storing Provider info
fname = os.path.join(ADDON_PATH_PROFILE, 'provider.info')
if os.path.isfile(fname):    
    provider_file = open(fname,'r')
    last_provider = provider_file.readline()
    provider_file.close()
    if MSO_ID != last_provider:
        CLEAR_SAVED_DATA()

provider_file = open(fname,'w')   
provider_file.write(MSO_ID)
provider_file.close()


#Event Colors
FREE = 'FF43CD80'
LIVE = 'FF00B7EB'
UPCOMING = 'FFFFB266'
FREE_UPCOMING = 'FFCC66FF'