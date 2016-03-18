import sys
import xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
import urllib, urllib2, httplib2
import json
import HTMLParser
import calendar
from datetime import datetime, timedelta
import time
import cookielib
import base64

from resources.globals import *
from resources.providers.adobe import ADOBE
from resources.providers.charter import CHARTER
from resources.providers.comcast import COMCAST
from resources.providers.dish import DISH
from resources.providers.direct_tv import DIRECT_TV
from resources.providers.twc import TWC
from resources.providers.verizon import VERIZON
from resources.providers.cable_one import CABLE_ONE
from resources.providers.optimum import OPTIMUM
from resources.providers.cox import COX
from resources.providers.bright_house import BRIGHT_HOUSE


def categories():           
    #addDir('Live & Upcoming','/live',1,ICON,FANART)
    addDir('Today\'s Games','/live',1,ICON,FANART)
    addDir('Archive Games','/live',2,ICON,FANART)
    #addDir('Featured',ROOT_URL+'mcms/prod/nbc-featured.json',2,ICON,FANART)
    #addDir('On NBC Sports','/replays',3,ICON,FANART)


def todaysGames(archive=None):
    '''
    {
        "brdcast": "40723",
        "id": "212",
        "loc": "207124",
        "parent": "",
        "per": "2",
        "ptsH": "93",
        "ptsV": "85",
        "recLH": "10",
        "recLV": "7",
        "recWH": "23",
        "recWV": "25",
        "reg": "2",
        "state": "4",
        "tba": "0",
        "time": "1458231300",
        "tmB": "460",
        "tmH": "193",
        "tmLabelB": "",
        "tmLabelT": "",
        "tmT": "193",
        "tmV": "460",
        "winnerBracket": "306",
        "winnerTB": "B",
        "rpyV": false,
        "radio": false,
        "rcpV": true,
        "preV": true,
        "video": false
      }
    '''
    url = 'http://data.ncaa.com/mml/2016/mobile/bracket.json'
    #print url
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

    tourn_day = json_source['bracket']['tournDay'] 
    teams = getTournamentInfo()         

    
    if not archive:
        setTodaysStream(tourn_day, json_source, teams)
    else:
        setArchiveStreams(tourn_day, json_source, teams)


    

def setTodaysStream(tourn_day, json_source, teams):
    tomorrow = str(int(tourn_day) + 86400)            
    current_games = getCurrentInfo()

    #Sort By Start Time
    json_source = sorted(json_source['bracket']['game'],key=lambda x:x['time'])
    
    for game in json_source:
        if game['time'] >= tourn_day and  game['time'] < tomorrow:        
            if game['tmT'] != '' and game['tmV'] != '':                
                game_id = game['id']                
                t_team_name, t_link_name = getTeamInfo(teams, game['tmT'])
                v_team_name, v_link_name = getTeamInfo(teams,game['tmV'])    
                game_time = time.strftime('%I:%M %p', time.localtime(int(game['time']))).lstrip('0')
                live_video = game['video']
                archive_video = game['rcpV']
                #print game_id + ' ' + live_video + ' ' + archive_video
                
                title = t_team_name + ' vs ' + v_team_name

                if NO_SPOILERS == '1' or NO_SPOILERS == '2':
                    name =  title
                else:
                    name =  t_team_name + ' ' + colorString(game['ptsH'], SCORE_COLOR) + ' vs ' + v_team_name + ' ' + colorString(game['ptsV'], SCORE_COLOR)

                if not live_video:
                    name =  colorString(game_time, UPCOMING) + ' ' + name

                else:
                    clock = getGameClock(current_games, game_id)
                    if clock == '':
                        clock = 'LIVE'
                    name =  colorString(clock,GAMETIME_COLOR) + ' ' + name

                
                link_url = ''

                #'http://i.turner.ncaa.com/sites/default/files/images/2016/03/17/duke-unc-wilmington-1.jpg'
                #fanart = 'http://i.turner.ncaa.com/sites/default/files/images/2016/03/17/'+t_link_name+'-uncw-1.jpg'
                #http://i.turner.ncaa.com/sites/default/files/cssu/mml/2016/games/[DIRECTION]/[TEAM-NAME-SAFE].jpg?cachebust=1426166870
                #http://i.turner.ncaa.com/sites/default/files/cssu/mml/2016/games/R/duke.jpg
                #print game['video']                
                addStream(name,link_url,title,game_id,icon=None,fanart=None)



def setArchiveStreams(tourn_day, json_source, teams):
    json_source = sorted(json_source['bracket']['game'],key=lambda x:x['time'], reverse=True)
    for game in json_source:        
        if game['time'] < tourn_day:
            if game['tmT'] != '' and game['tmV'] != '':                
                game_id = game['id']                
                t_team_name, t_link_name = getTeamInfo(teams, game['tmT'])
                v_team_name, v_link_name = getTeamInfo(teams,game['tmV'])    
                game_time = time.strftime('%I:%M %p', time.localtime(int(game['time']))).lstrip('0')
                live_video = game['video']
                archive_video = game['rcpV']
                
                title = t_team_name + ' vs ' + v_team_name

                if NO_SPOILERS == '1' or NO_SPOILERS == '3':
                    name =  title
                else:
                    name =  t_team_name + ' ' + colorString(game['ptsH'], SCORE_COLOR) + ' vs ' + v_team_name + ' ' + colorString(game['ptsV'], SCORE_COLOR)
                

                name =  colorString('FINAL ',FINAL) + name

                
                link_url = ''

                #'http://i.turner.ncaa.com/sites/default/files/images/2016/03/17/duke-unc-wilmington-1.jpg'
                #fanart = 'http://i.turner.ncaa.com/sites/default/files/images/2016/03/17/'+t_link_name+'-uncw-1.jpg'
                #http://i.turner.ncaa.com/sites/default/files/cssu/mml/2016/games/[DIRECTION]/[TEAM-NAME-SAFE].jpg?cachebust=1426166870
                #http://i.turner.ncaa.com/sites/default/files/cssu/mml/2016/games/R/duke.jpg
                #print game['video']                
                addStream(name,link_url,title,game_id,icon=None,fanart=None)

def startStream(game_id):
    '''

    ----------------------------------------------
    This gets the stream url and mediaAuth cookie
    ----------------------------------------------
    GET https://mm-ws.mms.ncaa.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3
    ?partnerParam1=PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8%2BPGF1dGhUb2tlbj48cmVzb3VyY2VJRD5UTlQ8L3Jlc291cmNlSUQ%2BPHRpdGxlSUQvPjxyZXF1ZXN0b3JJRD50dXJuZXI8L3JlcXVlc3RvcklEPjxpc3N1ZVRpbWU%2BMjAxNi0wMy0xN1QyMjowMTozMSswMDAwPC9pc3N1ZVRpbWU%2BPHR0bD4zMDAwMDA8L3R0bD48b3BhcXVlVXNlcklEPjYxM2U5OWJmMmRiNDc2MzA4ZjgwMjA5MWY4NDYyODE5PC9vcGFxdWVVc2VySUQ%2BPFNpZ25hdHVyZSB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI%2BPFNpZ25lZEluZm8%2BPENhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy14bWwtYzE0bi0yMDAxMDMxNSIvPjxTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjcnNhLXNoYTEiLz48UmVmZXJlbmNlIFVSST0iIj48VHJhbnNmb3Jtcz48VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz48L1RyYW5zZm9ybXM%2BPERpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNzaGExIi8%2BPERpZ2VzdFZhbHVlPld3Qi9jeXJCWklib1ZkVjZFRy9rMUxoN2VwMD08L0RpZ2VzdFZhbHVlPjwvUmVmZXJlbmNlPjwvU2lnbmVkSW5mbz48U2lnbmF0dXJlVmFsdWU%2BWDRKZmRyYXdVTGlPekZycjFRTFlmU2RmOXIrdFI5OEdoYkFXQW82bGVvZ2xoRCtCRWpyUVlzS0tVcGhJSUFOT0VHMnVERElwZEV6MgpyTXNjSjR4QUpTWE9VbnM2REJncnQxRWVnZGs5U2h2aTRLbzEwMC9lenFvaDY2Z1VuUWtPM0c1L0F1a29hTElqVFY1bUU4SVJ2cXhzClVkend0R3hvSnhPeHJ5Z29sY2M9PC9TaWduYXR1cmVWYWx1ZT48L1NpZ25hdHVyZT48L2F1dGhUb2tlbj4%3D
    &platform=IPHONE
    &playbackScenario=HTTP_CLOUD_IOS_TURNER
    &deviceId=6CF3EA47-BBE9-4C5B-A540-B7A3EB940589
    &subject=TURNER_MMOD_LIVE_VIDEO
    &auth=cookie
    &contentId=555183683 HTTP/1.1

    Host: mm-ws.mms.ncaa.com
    Proxy-Connection: keep-alive
    Accept: */*
    User-Agent: MML/43 CFNetwork/758.2.8 Darwin/15.0.0
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    '''
    print "MSO ID === "+  MSO_ID    
    provider = None
    if MSO_ID == 'Dish':
        provider = DISH()
    elif MSO_ID == 'TWC':
        provider = TWC()
    elif MSO_ID == 'Comcast_SSO':
        provider = COMCAST()
    elif MSO_ID == 'DTV':
        provider = DIRECT_TV()
    elif MSO_ID == 'Charter_Direct':
        provider = CHARTER()
    elif MSO_ID == 'Verizon':
        provider = VERIZON()
    elif MSO_ID == 'auth_cableone_net':
        provider = CABLE_ONE()
    elif MSO_ID == 'Cablevision':
        provider = OPTIMUM()
    elif MSO_ID == 'Cox':
        provider = COX()
    elif MSO_ID == 'Brighthouse':
        provider = BRIGHT_HOUSE()

    #provider = SET_PROVIDER()

    if provider != None:
        #stream_url = AUTHORIZE_STREAM(provider)
        
        adobe = ADOBE()
        expired_cookies = True
        try:
            cj = cookielib.LWPCookieJar()
            cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
            
            for cookie in cj:                
                if cookie.name == 'BIGipServerAdobe_Pass_Prod':
                    print cookie.name
                    print cookie.expires
                    print cookie.is_expired()
                    expired_cookies = cookie.is_expired()
        except:
            pass

        auth_token_file = os.path.join(ADDON_PATH_PROFILE, 'auth.token')  
        last_provider = ''
        fname = os.path.join(ADDON_PATH_PROFILE, 'provider.info')
        if os.path.isfile(fname):                
            provider_file = open(fname,'r') 
            last_provider = provider_file.readline()
            provider_file.close()

        print "Did cookies expire? " + str(expired_cookies)
        print "Does the auth token file exist? " + str(os.path.isfile(auth_token_file))
        print "Does the last provider match the current provider? " + str(last_provider == MSO_ID)
        print "Who was the last provider? " +str(last_provider)
                
        resource_id = GET_RESOURCE_ID()    
        #signed_requestor_id = GET_SIGNED_REQUESTOR_ID() 
        signed_requestor_id = 'kiDD4Lyj4et2/b9LXiOPs1k7mSjH622OwaeTR757WrmC43E19o3VBuMroNhGKVNh6YNFamJcRQ+BAern3zBaR/iRogwlVPhwu5eZnXMFI7FH1Hy0c3oVr/QhIFedgk36S5OTtYfUlm1+8Q2MXqcH/ON014MpC7dI+SmCK53jg8c='
       
        #If cookies are expired or auth token is not present run login or provider has changed
        if expired_cookies or not os.path.isfile(auth_token_file) or (last_provider != MSO_ID):
            #saml_request, relay_state, saml_submit_url = adobe.GET_IDP()            
            var_1, var_2, var_3 = provider.GET_IDP()  
            #Decode HTML
            var_3 = HTMLParser.HTMLParser().unescape(var_3)
            saml_response, relay_state = provider.LOGIN(var_1, var_2, var_3)
            #Error logging in. Abort! Abort!
            print "SAML RESPONSE:"
            print saml_response
            print "RELAY STATE:"
            print relay_state

            if saml_response == '' and relay_state == '':
                msg = "Please verify that your username and password are correct"
                dialog = xbmcgui.Dialog() 
                ok = dialog.ok('Login Failed', msg)
                return
            elif saml_response == 'captcha':
                msg = "Login requires captcha. Please try again later"
                dialog = xbmcgui.Dialog() 
                ok = dialog.ok('Captcha Found', msg)
                return

            adobe.POST_ASSERTION_CONSUMER_SERVICE(saml_response,relay_state)
            adobe.POST_SESSION_DEVICE(signed_requestor_id)    


        authz = adobe.POST_AUTHORIZE_DEVICE(resource_id,signed_requestor_id)      
        
        
        if 'Authorization failed' in authz or authz == '':
            msg = "Failed to authorize"
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Authorization Failed', msg)
            #Delete the invalid auth.token file
            fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
            os.remove(fname)
        else:
            media_token = adobe.POST_SHORT_AUTHORIZED(signed_requestor_id,authz)
            #stream_url = adobe.TV_SIGN(media_token,resource_id, stream_url)
            partnerParam1 = tokenTurner(media_token)
            stream_url = fetchStream(game_id, partnerParam1)
            #Set quality level based on user settings    
            #stream_url = SET_STREAM_QUALITY(stream_url) 
            listitem = xbmcgui.ListItem(path=stream_url)        
            xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=listitem)



def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param


params=get_params()
url=None
name=None
mode=None
game_id=None
icon_image = None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    game_id=urllib.unquote_plus(params["game_id"])
except:
    pass
try:
    icon_image=urllib.unquote_plus(params["icon_image"])
except:
    pass


print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "game_id:"+str(game_id)
print "icon image:"+str(icon_image)


if mode==None:        
    categories()        
elif mode==1:        
    todaysGames() 
elif mode==2:
    todaysGames(archive=True)
elif mode==104:    
    if USERNAME != '' and PASSWORD != '':
        startStream(game_id)
    else:
        msg = "A valid username and password is required to view streams. Please set these in the add-on settings."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Credentials Missing', msg)
        #sys.exit("Credentials not provided")
    

#Don't cache todays games
if mode==1:
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
else:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
