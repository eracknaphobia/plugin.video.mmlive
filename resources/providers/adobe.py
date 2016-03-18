from resources.globals import *


class ADOBE():    
    

    def GET_IDP(self):
        if not os.path.exists(ADDON_PATH_PROFILE):
            os.makedirs(ADDON_PATH_PROFILE)
        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
        
        #IDP_URL= 'https://sp.auth.adobe.com/adobe-services/authenticate?requestor_id=nbcsports&redirect_url=http://stream.nbcsports.com/nbcsn/index_nbcsn-generic.html?referrer=http://stream.nbcsports.com/liveextra/&domain_name=stream.nbcsports.com&mso_id=TWC&noflash=true&no_iframe=true'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Language", "en-us"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("User-Agent", UA_IPHONE)]
        
        resp = opener.open(IDP_URL)
        idp_source = resp.read()
        resp.close()
        #print idp_source
        #cj.save(ignore_discard=True);                
        SAVE_COOKIE(cj)

        idp_source = idp_source.replace('\n',"")        

        saml_request = FIND(idp_source,'<input type="hidden" name="SAMLRequest" value="','"')
        #print saml_request

        relay_state = FIND(idp_source,'<input type="hidden" name="RelayState" value="','"')

        saml_submit_url = FIND(idp_source,'action="','"')

        
        print saml_submit_url
        #print relay_state
        return saml_request, relay_state, saml_submit_url

    def POST_ASSERTION_CONSUMER_SERVICE(self,saml_response,relay_state):
        ###################################################################
        # SAML Assertion Consumer
        ###################################################################        
        url = 'https://sp.auth.adobe.com/sp/saml/SAMLAssertionConsumer'
        
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)

        cookies = ''
        for cookie in cj:            
            #if (cookie.name == "BIGipServerAdobe_Pass_Prod" or cookie.name == "client_type" or cookie.name == "client_version" or cookie.name == "JSESSIONID" or cookie.name == "redirect_url") and cookie.domain == "sp.auth.adobe.com":
            if cookie.domain == "sp.auth.adobe.com":
                cookies = cookies + cookie.name + "=" + cookie.value + "; "


        http = httplib2.Http()
        http.disable_ssl_certificate_validation=True    
        headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "en-us",
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Proxy-Connection": "keep-alive",
                            "Connection": "keep-alive",
                            "Origin": ORIGIN,
                            "Referer": REFERER,
                            "Cookie": cookies,
                            "User-Agent": UA_IPHONE}


        body = urllib.urlencode({'SAMLResponse' : saml_response,
                                 'RelayState' : relay_state
                                 })

        
        response, content = http.request(url, 'POST', headers=headers, body=body)        
        print 'POST_ASSERTION_CONSUMER_SERVICE------------------------------------------------'
        print headers
        print body
        print response
        print content
        print '-------------------------------------------------------------------------------'
        
    

    def POST_SESSION_DEVICE(self,signed_requestor_id):
        ###################################################################
        # Create a Session for Device
        ###################################################################                
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        
        cookies = ''
        for cookie in cj:
            #Possibly two JSESSION cookies being passed, may need to fix
            #if cookie.name == "BIGipServerAdobe_Pass_Prod" or cookie.name == "client_type" or cookie.name == "client_version" or cookie.name == "JSESSIONID" or cookie.name == "redirect_url":
            if (cookie.name == "BIGipServerAdobe_Pass_Prod" or cookie.name == "client_type" or cookie.name == "client_version" or cookie.name == "JSESSIONID" or cookie.name == "redirect_url") and cookie.path == "/":
                cookies = cookies + cookie.name + "=" + cookie.value + "; "
        '''
        POST https://sp.auth.adobe.com/adobe-services/1.0/sessionDevice HTTP/1.1
        Host: sp.auth.adobe.com
        Accept: */*
        Content-Type: application/x-www-form-urlencoded
        Connection: keep-alive
        Proxy-Connection: keep-alive
        Cookie: BIGipServerAdobe_Pass_Prod=388119306.20480.0000;JSESSIONID=5B907E6216A92CCC58A24426F1F47D6C;passgw=gw-us-east-1;
        User-Agent: AdobePassNativeClient/1.9.4 (iPhone; U; CPU iPhone OS 9.2.1 like Mac OS X; en-us)
        Content-Length: 312
        Accept-Language: en-us
        Accept-Encoding: gzip, deflate

        requestor_id=MML&_method=GET&signed_requestor_id=kiDD4Lyj4et2%2Fb9LXiOPs1k7mSjH622OwaeTR757WrmC43E19o3VBuMroNhGKVNh6YNFamJcRQ%2BBAern3zBaR%2FiRogwlVPhwu5eZnXMFI7FH1Hy0c3oVr%2FQhIFedgk36S5OTtYfUlm1%2B8Q2MXqcH%2FON014MpC7dI%2BSmCK53jg8c%3D
        &device_id=d41e9eac8874603be3fcdb9c7247fe7e2dce356f1b8ebd0198fefb57f2b4ea1b
        '''
        url = 'https://sp.auth.adobe.com//adobe-services/1.0/sessionDevice'
        http = httplib2.Http()
        http.disable_ssl_certificate_validation=True    
        headers = { "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-us",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Proxy-Connection": "keep-alive",
                    "Connection": "keep-alive",                                                
                    "Cookie": cookies,
                    "User-Agent": UA_ADOBE_PASS}

        data = urllib.urlencode({'requestor_id' : 'MML',
                                 '_method' : 'GET',
                                 'signed_requestor_id' : signed_requestor_id,
                                 'device_id' : DEVICE_ID
                                })
        
       
        response, content = http.request(url, 'POST', headers=headers, body=data)
        print 'POST_SESSION_DEVICE------------------------------------------------------------'
        print headers
        print data
        print response
        print content
        print '-------------------------------------------------------------------------------'
        
        auth_token = FIND(content,'<authnToken>','</authnToken>')
        print "AUTH TOKEN"        
        print auth_token
        auth_token = auth_token.replace("&lt;", "<")
        auth_token = auth_token.replace("&gt;", ">")
        # this has to be last:
        auth_token = auth_token.replace("&amp;", "&")
        print auth_token

        #Save auth token to file for         
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        #if not os.path.isfile(fname):            
        device_file = open(fname,'w')   
        device_file.write(auth_token)
        device_file.close()

        #return auth_token, session_guid        
   

    def POST_AUTHORIZE_DEVICE(self,resource_id,signed_requestor_id):
        ###################################################################
        # Authorize Device
        ###################################################################
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        device_file = open(fname,'r') 
        auth_token = device_file.readline()
        device_file.close()
        
        if auth_token == '':
            return ''

        url = 'https://sp.auth.adobe.com//adobe-services/1.0/authorizeDevice'
        http = httplib2.Http()
        http.disable_ssl_certificate_validation=True    
        headers = {"Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-us",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Proxy-Connection": "keep-alive",
                    "Connection": "keep-alive",                                                                
                    "User-Agent": UA_ADOBE_PASS}

        '''
        POST https://sp.auth.adobe.com/adobe-services/1.0/authorizeDevice HTTP/1.1
        Host: sp.auth.adobe.com
        Accept: */*
        Content-Type: application/x-www-form-urlencoded; charset=UTF-8
        Connection: keep-alive
        Proxy-Connection: keep-alive
        Cookie: 
        User-Agent: AdobePassNativeClient/1.9.4 (iPhone; U; CPU iPhone OS 9.2.1 like Mac OS X; en-us)
        Content-Length: 1430
        Accept-Language: en-us
        Accept-Encoding: gzip, deflate


        resource_id=TNT
        &requestor_id=MML
        &signed_requestor_id=kiDD4Lyj4et2%2Fb9LXiOPs1k7mSjH622OwaeTR757WrmC43E19o3VBuMroNhGKVNh6YNFamJcRQ%2BBAern3zBaR%2FiRogwlVPhwu5eZnXMFI7FH1Hy0c3oVr%2FQhIFedgk36S5OTtYfUlm1%2B8Q2MXqcH%2FON014MpC7dI%2BSmCK53jg8c%3D
        &mso_id=TempPass
        &authentication_token=%3CsignatureInfo%3EY0tacTbt6J9%2FvqJWZLGFs4UL8w4kpEN3%2FRCqCgi7ta8n0MgbgWkKTPdnQMRkDUceZezBXFcrFftbdeAN8PkaZz5H6bF93%2Bcdt5nznH1vyKb90dcorLxAgF%2BxUbVnqk6F29V5ARTce6%2Bu8fHBAqzYyiLpYN8yZDoT%2F3UEWz3CGqw%3D%3CsignatureInfo%3E%3CsimpleAuthenticationToken%3E%3CsimpleTokenAuthenticationGuid%3E98b669aeab04eb8398a35d999ef65d6a%3C%2FsimpleTokenAuthenticationGuid%3E%3CsimpleSamlSessionIndex%3E0XEThQfyW5yOFn5%2B4GBReoziz8aNdYNDBqG6%2FDUJTLJJRN5LGMKmvDf1Sbp1YXts%3C%2FsimpleSamlSessionIndex%3E%3CsimpleTokenRequestorID%3EMML%3C%2FsimpleTokenRequestorID%3E%3CsimpleTokenDomainName%3Eadobe.com%3C%2FsimpleTokenDomainName%3E%3CsimpleTokenExpires%3E2016%2F07%2F15%2010%3A14%3A39%20GMT%20-0700%3C%2FsimpleTokenExpires%3E%3CsimpleTokenMsoID%3ETempPass%3C%2FsimpleTokenMsoID%3E%3CsimpleTokenDeviceID%3E%3CsimpleTokenFingerprint%3Ef00a427b58d5a62ad071eb66bd65b185d4a92ebb%3C%2FsimpleTokenFingerprint%3E%3C%2FsimpleTokenDeviceID%3E%3CsimpleSamlNameID%3E0XEThQfyW5yOFn5%2B4GBReoziz8aNdYNDBqG6%2FDUJTLJJRN5LGMKmvDf1Sbp1YXts%3C%2FsimpleSamlNameID%3E%3C%2FsimpleAuthenticationToken%3E
        &device_id=8be8584b0b262ce451ccf087adc4c7d931d26ce8cc7275ff799f1a03e262d18d
        &userMeta=1
        '''
        data = urllib.urlencode({'requestor_id' : 'MML',
                                 'resource_id' : 'TNT',
                                 'signed_requestor_id' : signed_requestor_id,
                                 'mso_id' : MSO_ID,
                                 'authentication_token' : auth_token,
                                 'device_id' : DEVICE_ID,
                                 'userMeta' : '1'                             
                                })
        
        
        response, content = http.request(url, 'POST', headers=headers, body=data)
        
        print 'POST_AUTHORIZE_DEVICE------------------------------------------------------------'
        print headers
        print data
        print response
        print content
        print '-------------------------------------------------------------------------------'

        try:
            print "REFRESHED COOKIE"
            adobe_pass = response['set-cookie']
            print adobe_pass
            cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
            cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
            #BIGipServerAdobe_Pass_Prod=526669578.20480.0000; expires=Fri, 19-Jun-2015 19:58:42 GMT; path=/
            value = FIND(adobe_pass,'BIGipServerAdobe_Pass_Prod=',';')
            expires = FIND(adobe_pass,'expires=',' GMT;')
            #date_time = '29.08.2011 11:05:02'        
            #pattern = '%d.%m.%Y %H:%M:%S'
            #Fri, 19-Jun-2015 19:58:42
            pattern = '%a, %d-%b-%Y %H:%M:%S'
            print expires
            expires_epoch = int(time.mktime(time.strptime(expires, pattern)))
            print expires_epoch
            ck = cookielib.Cookie(version=0, name='BIGipServerAdobe_Pass_Prod', value=value, port=None, port_specified=False, domain='sp.auth.adobe.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=expires_epoch, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
            cj.set_cookie(ck)
            #cj.save(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True);
            SAVE_COOKIE(cj)

        except:
            pass
        authz = FIND(content,'<authzToken>','</authzToken>')                
        authz = authz.replace("&lt;", "<")
        authz = authz.replace("&gt;", ">")
        # this has to be last:
        authz = authz.replace("&amp;", "&")
        print "AUTH Z TOKEN"
        print authz
        
        return authz


    def POST_SHORT_AUTHORIZED(self,signed_requestor_id,authz):
        ###################################################################
        # Short Authorize Device
        ###################################################################
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        device_file = open(fname,'r') 
        auth_token = device_file.readline()
        device_file.close()

        session_guid = FIND(auth_token,'<simpleTokenAuthenticationGuid>','</simpleTokenAuthenticationGuid>')
        print "SESSION GUID"
        print session_guid    

        url = 'https://sp.auth.adobe.com//adobe-services/1.0/deviceShortAuthorize'
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),                                                                            
                            ("User-Agent", UA_ADOBE_PASS)]
        

        data = urllib.urlencode({'requestor_id' : 'MML',                             
                                 'signed_requestor_id' : signed_requestor_id,
                                 'mso_id' : MSO_ID,
                                 'session_guid' : session_guid,
                                 'hashed_guid' : 'false',
                                 'authz_token' : authz,
                                 'device_id' : DEVICE_ID
                                })

        resp = opener.open(url, data)
        media_token = resp.read()
        resp.close()    
        print media_token

        return media_token



    def TV_SIGN(self, media_token, resource_id, stream_url):    
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        #print cj
        cookies = ''
        for cookie in cj:        
            if cookie.name == "BIGipServerAdobe_Pass_Prod" or cookie.name == "JSESSIONID":
                cookies = cookies + cookie.name + "=" + cookie.value + "; "

        url = 'http://sp.auth.adobe.com//tvs/v1/sign'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en;q=1"),
                            ("Content-Type", "application/x-www-form-urlencoded"),                                                                                         
                            ("Cookie", cookies),
                            ("User-Agent", "NBCSports/4.2.0 (iPhone; iOS 8.3; Scale/2.00)")]
        

        data = urllib.urlencode({'cdn' : 'akamai',
                                 'mediaToken' : base64.b64encode(media_token),
                                 'resource' : base64.b64encode(resource_id),
                                 'url' : stream_url
                                })

        resp = opener.open(url, data)
        url = resp.read()
        resp.close()    
        
        return url
        