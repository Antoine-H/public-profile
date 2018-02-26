# -*- coding: utf-8 -*-
#!/usr/bin/python3

#
# Forked from github.com/milo2012/osintstalker
# No license specified by original author.
#
# Example: `python3 fb.py -user FBID`
#
# TODO: Parse ID post from timeline better.
#       GraphML - Maltego ?
#

import httplib2,json
import zipfile
import sys
import re
import time
import datetime
import operator
import sqlite3
import os
from datetime import datetime
import requests
from termcolor import colored, cprint
from pygraphml import *
from pygraphml.graph import *
from pygraphml.node import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from io import StringIO


requests.adapters.DEFAULT_RETRIES = 10

h = httplib2.Http(".cache")

facebook_username     = ""
facebook_password     = ""
facebook_access_token = ""

uid            = ""
username       = ""
internetAccess = True
cookies        = {}
all_cookies    = {}
reportFileName = ""

#Gathers likes across Photos Likes and Post Likes
peopleIDList      = []
likesCountList    = []
timeOfPostList    = []
placesVisitedList = []

#Chromium Options
chromeOptions = webdriver.ChromeOptions()
prefs  = {"profile.managed_default_content_settings.images":2,
          "profile.default_content_setting_values.notifications":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)


def createDatabase():
    conn = sqlite3.connect("facebook.db")
    c    = conn.cursor()
    sql  = ("create table if not exists photosLiked (sourceUID TEXT, "
            "description TEXT, photoURL TEXT unique, pageURL TEXT, username "
            "TEXT)")
    sql1 = ("create table if not exists photosCommented (sourceUID TEXT, "
            "description TEXT, photoURL TEXT unique, pageURL TEXT, username "
            "TEXT)")
    sql2 = ("create table if not exists friends (sourceUID TEXT, name TEXT, "
            "userName TEXT unique, month TEXT, year TEXT)")
    sql3 = ("create table if not exists friendsDetails (sourceUID TEXT, "
            "userName TEXT unique, userEduWork TEXT, userLivingCity TEXT, "
            "userCurrentCity TEXT, userLiveEvents TEXT, userGender TEXT, "
            "userStatus TEXT, userGroups TEXT)")
    sql4 = ("create table if not exists videosBy (sourceUID TEXT, title TEXT "
            "unique, url TEXT)")
    sql5 = ("create table if not exists pagesLiked (sourceUID TEXT, name TEXT "
            "unique, category TEXT,url TEXT)")
    sql6 = ("create table if not exists photosOf (sourceUID TEXT, description "
            "TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)")
    sql7 = ("create table if not exists photosBy (sourceUID TEXT, description "
            "TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)")

    c.execute(sql)
    c.execute(sql1)
    c.execute(sql2)
    c.execute(sql3)
    c.execute(sql4)
    c.execute(sql5)
    c.execute(sql6)
    c.execute(sql7)
    conn.commit()


createDatabase()
conn = sqlite3.connect("facebook.db")


# NOT WORKING YET.
def createMaltego(username):
    g = Graph()
    totalCount = 50
    start      = 0
    nodeList   = []
    edgeList   = []

    while start < totalCount:
        nodeList.append("")
        edgeList.append("")
        start += 1

    nodeList[0]         = g.add_node("Facebook_"+username)
    nodeList[0]["node"] = createNodeFacebook(username,
                                    "https://www.facebook.com/"+username,uid)

    counter1 = 1
    counter2 = 0
    userList = []

    c = conn.cursor()
    c.execute("select userName from friends where sourceUID=?",(uid,))
    dataList = c.fetchall()
    nodeUid  = ""
    for i in dataList:
        if i[0] not in userList:
            userList.append(i[0])
            try:
                nodeUid = str(convertUser2ID(driver,str(i[0])))
                nodeList[counter1] = g.add_node("Facebook_"+str(i[0]))
                nodeList[counter1]["node"] = createNodeFacebook(i[0],
                                "https://www.facebook.com/"+str(i[0]),nodeUid)
                edgeList[counter2] = g.add_edge(nodeList[0],nodeList[counter1])
                edgeList[counter2]["link"] = createLink("Facebook")
                nodeList.append("")
                edgeList.append("")
                counter1 += 1
                counter2 += 1
            except IndexError:
                continue
    if len(nodeUid) > 0:
        parser = GraphMLParser()
        if not os.path.exists(os.getcwd()+"/Graphs"):
            os.makedirs(os.getcwd()+"/Graphs")
        filename = "Graphs/Graph1.graphml"
        parser.write(g, "Graphs/Graph1.graphml")
        cleanUpGraph(filename)
        filename = username+"_maltego.mtgx"
        print("Creating archive: ", filename)
        zf = zipfile.ZipFile(filename, mode="w")
        print("Adding Graph1.graphml")
        zf.write("Graphs/Graph1.graphml")
        print("Closing")
        zf.close()


# NOT WORKING YET.
def createLink(label):
    xmlString  = ('<mtg:MaltegoLink '
                  'xmlns:mtg="http://maltego.paterva.com/xml/mtgx" '
                  'type="maltego.link.manual-link">')
    xmlString += ('<mtg:Properties>')
    xmlString += ('<mtg:Property displayName="Description" '
                  'hidden="false" name="maltego.link.manual.description" '
                  'nullable="true" readonly="false" type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Style" hidden="false" '
                  'name="maltego.link.style" nullable="true" '
                  'readonly="false" type="int">')
    xmlString += ('<mtg:Value>0</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Label" hidden="false" '
                  'name="maltego.link.manual.type" nullable="true" '
                  'readonly="false" type="string">')
    xmlString += ('<mtg:Value>'+label+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Show Label" hidden="false" '
                  'name="maltego.link.show-label" nullable="true" '
                  'readonly="false" type="int">')
    xmlString += ('<mtg:Value>0</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Thickness" hidden="false" '
                  'name="maltego.link.thickness" nullable="true" '
                  'readonly="false" type="int">')
    xmlString += ('<mtg:Value>2</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Color" hidden="false" '
                  'name="maltego.link.color" nullable="true" '
                  'readonly="false" type="color">')
    xmlString += ('<mtg:Value>8421505</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('</mtg:Properties>')
    xmlString += ('</mtg:MaltegoLink>')
    return xmlString


# NOT WORKING YET.
def createNodeImage(name,url):
    xmlString =  ('<mtg:MaltegoEntity '
                  'xmlns:mtg="http://maltego.paterva.com/xml/mtgx" '
                  'type="maltego.Image">')
    xmlString += ('<mtg:Properties>')
    xmlString += ('<mtg:Property displayName="Description" hidden="false" '
                  'name="description" nullable="true" readonly="false" '
                  'type="string">')
    xmlString += ('<mtg:Value>'+name+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="URL" hidden="false" name="url" '
                  'nullable="true" readonly="false" type="url">')
    xmlString += ('<mtg:Value>'+url+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('</mtg:Properties>')
    xmlString += ('</mtg:MaltegoEntity>')
    return xmlString


# NOT WORKING YET.
def createNodeFacebook(displayName,url,uid):
    xmlString  = ('<mtg:MaltegoEntity '
                  'xmlns:mtg="http://maltego.paterva.com/xml/mtgx" '
                  'type="maltego.affiliation.Facebook">')
    xmlString += ('<mtg:Properties>')
    xmlString += ('<mtg:Property displayName="Name" hidden="false" '
                  'name="person.name" nullable="true" readonly="false" '
                  'type="string">')
    xmlString += ('<mtg:Value>'+displayName+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Network" hidden="false" '
                  'name="affiliation.network" nullable="true" readonly="true" '
                  'type="string">')
    xmlString += ('<mtg:Value>Facebook</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="UID" hidden="false" '
                  'name="affiliation.uid" nullable="true" readonly="false" '
                  'type="string">')
    xmlString += ('<mtg:Value>'+str(uid)+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Profile URL" hidden="false" '
                  'name="affiliation.profile-url" nullable="true" '
                  'readonly="false" type="string">')
    xmlString += ('<mtg:Value>'+url+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('</mtg:Properties>')
    xmlString += ('</mtg:MaltegoEntity>')
    return xmlString


# NOT WORKING YET.
def createNodeUrl(displayName,url):
    xmlString  = ('<mtg:MaltegoEntity '
                  'xmlns:mtg="http://maltego.paterva.com/xml/mtgx"'
                  'type="maltego.URL">')
    xmlString += ('<mtg:Properties>')
    xmlString += ('<mtg:Property displayName="'+displayName+'" '
                  'hidden="false" name="short-title" nullable="true"'
                  'readonly="false" type="string">')
    xmlString += ('<mtg:Value>'+displayName+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="'+displayName+'" '
                  'hidden="false" name="url" nullable="true" readonly="false"'
                  'type="url">')
    xmlString += ('<mtg:Value>'+displayName+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Title" hidden="false" '
                  'name="title" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('</mtg:Properties>')
    xmlString += ('</mtg:MaltegoEntity>')
    return xmlString


# NOT WORKING YET.
def createNodeLocation(lat,lng):
    xmlString  = ('<mtg:MaltegoEntity '
                  'xmlns:mtg="http://maltego.paterva.com/xml/mtgx"'
                  'type="maltego.Location">')
    xmlString += ('<mtg:Properties>')
    xmlString += ('<mtg:Property displayName="Name" hidden="false" '
                  'name="location.name" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value>lat='+str(lat)+' lng='+str(lng)+'</mtg:Value>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Area Code" hidden="false" '
                  'name="location.areacode" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Area" hidden="false" '
                  'name="location.area" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Latitude" hidden="false" '
                  'name="latitude" nullable="true" readonly="false"'
                  'type="float">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Longitude" hidden="false" '
                  'name="longitude" nullable="true" readonly="false"'
                  'type="float">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Country" hidden="false" '
                  'name="country" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Country Code" hidden="false" '
                  'name="countrycode" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="City" hidden="false" '
                  'name="city" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('<mtg:Property displayName="Street Address" hidden="false" '
                  'name="streetaddress" nullable="true" readonly="false"'
                  'type="string">')
    xmlString += ('<mtg:Value/>')
    xmlString += ('</mtg:Property>')
    xmlString += ('</mtg:Properties>')
    xmlString += ('</mtg:MaltegoEntity>')
    return xmlString


# NOT WORKING YET.
def cleanUpGraph(filename):
    newContent = []
    with open(filename) as f:
        content = f.readlines()
        for i in content:
            if '<key attr.name="node" attr.type="string" id="node"/>' in i:
                i = i.replace('name="node" attr.type="string"',
                              'name="MaltegoEntity" for="node"')
            if '<key attr.name="link" attr.type="string" id="link"/>' in i:
                i = i.replace('name="link" attr.type="string"',
                              'name="MaltegoLink" for="edge"')
            i = i.replace("&lt;","<")
            i = i.replace("&gt;",">")
            i = i.replace("&quot;",'"')
            newContent.append(i.strip())

    f = open(filename,"w")
    for item in newContent:
        f.write("%s\n" % item)
    f.close()


def convertUser2ID(driver, username):
    filename = username+".html"
    if not os.path.lexists(filename):
        url  = "https://www.facebook.com/"+username
        driver.get(url)
        html = driver.page_source
    else:
        html = open(filename).read()
    soup = BeautifulSoup(html, "lxml")
    uid  = soup.find_all("div" ,{"class": "_5h60"})
    return uid[0]["data-gt"].split('"')[3]


def loginFacebook(driver):
    driver.implicitly_wait(120)
    driver.get("https://www.facebook.com/")
    assert "Facebook" in driver.title
    time.sleep(3)
    driver.find_element_by_id("email").send_keys(facebook_username)
    driver.find_element_by_id("pass").send_keys(facebook_password)
    driver.find_element_by_id("loginbutton").click()
    global all_cookies
    all_cookies = driver.get_cookies()
    html = driver.page_source
    if "Incorrect Email/Password Combination" in html:
        print("[!] Incorrect Facebook username (email address) or password")
        sys.exit()


def write2Database(dbName,dataList):
    try:
        print("[*] Writing ", str(len(dataList)),
              " record(s) to database table: ", dbName)
        numOfColumns = len(dataList[0])
        c = conn.cursor()
        if numOfColumns == 3:
            for i in dataList:
                try:
                    c.execute("INSERT INTO "+dbName+" VALUES (?,?,?)", i)
                    conn.commit()
                except sqlite3.IntegrityError:
                    continue
        if numOfColumns == 4:
            for i in dataList:
                try:
                    c.execute("INSERT INTO "+dbName+" VALUES (?,?,?,?)", i)
                    conn.commit()
                except sqlite3.IntegrityError:
                    continue
        if numOfColumns == 5:
            for i in dataList:
                try:
                    c.execute("INSERT INTO "+dbName+" VALUES (?,?,?,?,?)", i)
                    conn.commit()
                except sqlite3.IntegrityError:
                    continue
        if numOfColumns == 9:
            for i in dataList:
                try:
                    c.execute("INSERT INTO "+dbName+
                              " VALUES (?,?,?,?,?,?,?,?,?)", i)
                    conn.commit()
                except sqlite3.IntegrityError:
                    continue
    except TypeError as e:
        print(e)
        pass
    except IndexError as e:
        print(e)
        pass


def downloadFile(url):
    global cookies
    for s_cookie in all_cookies:
        cookies[s_cookie["name"]] = s_cookie["value"]
    r = requests.get(url,cookies=cookies)
    html = r.content
    return html


def downloadPage(driver,userid, url, username, id):
    if   url == "timeline":
        url = "https://www.facebook.com/"+username.strip()
    elif url == "post":
        url = "https://www.facebook.com/"+username+"/posts/"+str(id)
    elif url == "likes":
        url = ("https://www.facebook.com/ufi/reaction/profile/browser/"
               "?ft_ent_identifier="+str(id))
    else:
        url = "https://www.facebook.com/search/"+str(userid).strip()+"/"+url
    driver.get(url)
    if "This page isn't available" in driver.page_source:
        print("[!] Cannot access page ", url)
        return ""
    lenOfPage = driver.execute_script("window.scrollTo(0, "
                "document.body.scrollHeight);"
                "var lenOfPage=document.body.scrollHeight;"
                "return lenOfPage;")
    match = False
    while match == False:
        time.sleep(4)
        lastCount = lenOfPage
        lenOfPage = driver.execute_script("window.scrollTo(0, "
                    "document.body.scrollHeight);"
                    "var lenOfPage=document.body.scrollHeight;"
                    "return lenOfPage;")
        if lastCount == lenOfPage:
            match = True
    return driver.page_source


def download(filename, type, username, id=0):
    if not os.path.lexists(filename):
        if   type == "places-visited":
            print("[*] Caching places visited by: ", username)
        elif type == "places-liked":
            print("[*] Caching places liked by: ", username)
        elif type == "videos-by":
            print("[*] Caching videos by: ", username)
        elif type == "info":
            print("[*] Caching informations about: ", username)
        elif type == "photos-by":
            print("[*] Caching photos by: ", username)
        elif type == "photos-of":
            print("[*] Caching photos of: ", username)
        elif type == "photos-commented":
            print("[*] Caching photos commented by: ", username)
        elif type == "photos-liked":
            print("[*] Caching photos liked by: ", username)
        elif type == "pages-liked":
            print("[*] Caching pages liked by: ", username)
        elif type == "friends":
            print("[*] Caching friendlist of: ", username)
        elif type == "apps-used":
            print("[*] Caching applications used by: ", username)
        elif type == "timeline":
            print("[*] Crawling timeline")
        elif type == "post":
            print("[*] Caching post: ", str(id))
        elif type == "liked":
            print("[*] Caching post likes: ", str(id))
        html      = downloadPage(driver, uid, type, username, id)
        text_file = open(filename, "w")
        text_file.write(str(html))
        text_file.close()
    else:
        html = open(filename, "r").read()
    return html


def parsePost(id,username):
    global placesVisitedList
    filename = "posts__"+str(id)
    html1 = download(filename, "post", username, id)
    soup1    = BeautifulSoup(html1, "lxml")
    htmlList = soup1.find("abbr",{"class" : "_5ptz"})
    tlTime   = soup1.find("abbr")

    if " at " in str(htmlList):
        soup2          = BeautifulSoup(str(htmlList), "lxml")
        locationList   = soup2.find_all("a",{"class" : "profileLink"})
        locURL         = ""
        locDescription = ""
        locTime        = tlTime["data-utime"]
        placesVisitedList.append([locTime,locDescription,locURL])


def parseLikesPosts(id):
    peopleID = []
    filename = "likes_"+str(id)
    html1 = download(filename, "likes", username, id)
    soup1          = BeautifulSoup(html1, "lxml")
    peopleLikeList = soup1.find_all("div",{"class" : "_5j0e fsl fwb fcb"})

    if len(peopleLikeList) > 0:
        print("[*] Extracting Likes from Post: ", str(id))
        for x in peopleLikeList:
            soup2        = BeautifulSoup(str(x), "lxml")
            peopleLike   = soup2.find("a")
            peopleLikeID = peopleLike["href"].split("?")[0].replace(
                                                "https://www.facebook.com/","")
            if peopleLikeID == "profile.php":
                r = re.compile("id=(.*?)&fref")
                m = r.search(str(peopleLike["href"]))
                if m:
                    peopleLikeID = m.group(1)
            print("[*] Liked Post: ", "\t", peopleLikeID)
            if peopleLikeID not in peopleID:
                peopleID.append(peopleLikeID)

    return peopleID


def parseTimeline(html, username):
    global timeOfPostList
    global peopleIDList
    soup      = BeautifulSoup(html, "lxml")
    posts     = soup.find_all("div",
                        {"class" : "_4-u2 mbm _4mrt _5jmm _5pat _5v3q _4-u8"})
    ids       = str(soup.find_all("script")[-25])
    posts_ids = []
    while ids:
        try:
            index = ids.index("story_token")
            posts_ids.append(ids[index+31:index+48])
            ids = ids[index+48:]
        except ValueError:
            ids = ""
            continue

    print(len(posts), len(posts_ids))
    for post in posts:
        unixTime  = post.find("abbr")["data-utime"]
        localTime = \
        (datetime.fromtimestamp(int(unixTime)).strftime("%Y-%m-%d %H:%M:%S"))
        timeOfPost = localTime
        timeOfPostList.append(localTime)

        print("[*] Time of post: ", localTime)

    for post in posts_ids:
        parsePost(post,username)
        peopleIDLikes = parseLikesPosts(post)
        try:
            for id1 in peopleIDLikes:
                global likesCountList
                if id1 in peopleIDList:
                    lastCount = 0
                    position = peopleIDList.index(id1)
                    likesCountList[position] += 1
                else:
                    peopleIDList.append(id1)
                    likesCountList.append(1)
        except TypeError:
            continue


    print("\n")

def writeReport(username):
    global likesCountList
    global placesVisitedList
    global timeOfPostList
    global reportFileName
    global peopleIDList
    if len(reportFileName) < 1:
        reportFileName = username+"_report.txt"
    reportFile = open(reportFileName, "w")

    reportFile.write("\n********** Places visited by "+str(username)+
                     " **********\n")
    filename = username+"_placesVisited.html"
    html     = download(filename, "places-visited", username)
    dataList = parsePlaces(html)
    for i in dataList:
        reportFile.write(i[2]+"\t"+i[1]+"\t"+i[3]+"\n")

    reportFile.write("\n********** Places liked by "+str(username)+
                     " **********\n")
    filename = username+"_placesLiked.html"
    html     = download(filename, "places-liked", username)
    dataList = parsePlaces(html)
    for i in dataList:
        reportFile.write(str(i[2])+"\t"+str([1])+"\t"+str(i[3])+"\n")

    reportFile.write("\n********** Places checked in **********\n")
    for places in placesVisitedList:
        unixTime  = places[0]
        localTime = \
        (datetime.fromtimestamp(int(unixTime)).strftime("%Y-%m-%d %H:%M:%S"))
        reportFile.write(localTime+"\t"+places[1]+"\t"+places[2]+"\n")

    reportFile.write("\n********** Apps used by "+str(username)+
                     " **********\n")
    filename = username+"_apps.html"
    html     = download(filename, "apps-used", username)
    dataList = parseAppsUsed(html)
    result = ""
    for x in dataList:
        reportFile.write(x+"\n")
        x = x.lower()
        if "blackberry" in x:
            result += "[*] User is using a Blackberry device\n"
        if "android" in x:
            result += "[*] User is using an Android device\n"
        if "ios" in x or "ipad" in x or "iphone" in x:
            result += "[*] User is using an iOS Apple device\n"
        if "samsung" in x:
            result += "[*] User is using a Samsung Android device\n"
    reportFile.write(result)

    reportFile.write("\n********** Videos posted by "+str(username)+
                     " **********\n")
    filename = username+"_videosBy.html"
    html     = download(filename, "videos-by", username)
    dataList = parseVideosBy(html)
    for i in dataList:
        reportFile.write(i[2]+"\t"+i[1]+"\n")

    reportFile.write("\n********** Pages liked by "+str(username)+
                     " **********\n")
    filename = username+"_pages.html"
    html     = download(filename, "pages-liked", username)
    dataList = parsePagesLiked(html)
    for i in dataList:
        pageName = i[0]
        tmpStr	 = i[2]+"\t"+i[1]+"\t"+i[3]+"\n"
        reportFile.write(pageName+"\t"+tmpStr)
    print("\n")

    c = conn.cursor()
    reportFile.write("\n********** Friendship history of "+str(username)+
                     " **********\n")
    c.execute("select * from friends where sourceUID=?",(uid,))
    dataList = c.fetchall()
    try:
        if len(str(dataList[0][4]))>0:
            for i in dataList:
                #Date First followed by Username
                reportFile.write(i[4]+"\t"+i[3]+"\t"+i[2]+"\t"+i[1]+"\n")
        print("\n")
    except IndexError:
        pass

    reportFile.write("\n********** Friends of "+str(username)+" **********\n")
    reportFile.write("*** Backtracing from Facebook likes/comments/tags "
                     "***\n\n")
    c = conn.cursor()
    c.execute("select userName from friends where sourceUID=?",(uid,))
    dataList = c.fetchall()
    for i in dataList:
        reportFile.write(str(i[0])+"\n")
    print("\n")

    tempList = []
    totalLen = len(timeOfPostList)
    timeSlot1 = 0
    timeSlot2 = 0
    timeSlot3 = 0
    timeSlot4 = 0
    timeSlot5 = 0
    timeSlot6 = 0
    timeSlot7 = 0
    timeSlot8 = 0

    count = 0
    if len(peopleIDList) > 0:
        likesCountList, peopleIDList = \
                zip(*sorted(zip(likesCountList,peopleIDList),reverse=True))

        reportFile.write("\n********** Analysis of Facebook post likes "
                         "**********\n")
        while count < len(peopleIDList):
            testStr = str(likesCountList[count])+"\t"+str(peopleIDList[count])
            reportFile.write(testStr+"\n")
            count += 1

    reportFile.write("\n********* Analysis of interactions between "
                     +str(username)+" and friends *********\n")
    c = conn.cursor()
    c.execute("select userName from friends where sourceUID=?",(uid,))
    dataList = c.fetchall()
    photosliked     = []
    photoscommented = []
    userID          = []

    photosLikedUser      = []
    photosLikedCount     = []
    photosCommentedUser  = []
    photosCommentedCount = []

    for i in dataList:
        c.execute("select * from photosLiked where "
                  "sourceUID=? and username=?",(uid,i[0],))
        dataList1 = []
        dataList1 = c.fetchall()
        if len(dataList1) > 0:
            photosLikedUser.append(i[0])
            photosLikedCount.append(len(dataList1))
    for i in dataList:
        c.execute("select * from photosCommented "
                  "where sourceUID=? and username=?",(uid,i[0],))
        dataList1 = []
        dataList1 = c.fetchall()
        if len(dataList1) > 0:
            photosCommentedUser.append(i[0])
            photosCommentedCount.append(len(dataList1))
    if(len(photosLikedCount)>1):
        reportFile.write("Photo likes: "+str(username)+" and friends\n")
        photosLikedCount, photosLikedUser = \
            zip(*sorted(zip(photosLikedCount, photosLikedUser),reverse=True))
        count = 0
        while count < len(photosLikedCount):
            tmpStr = (str(photosLikedCount[count])+"\t"
                        +photosLikedUser[count]+"\n")
            count += 1
            reportFile.write(tmpStr)
    if(len(photosCommentedCount)>1):
        reportFile.write("\n********** Comments on "+str(username)+
                         "'s photos **********\n")
        photosCommentedCount, photosCommentedUser = \
                zip(*sorted(zip(photosCommentedCount,
                            photosCommentedUser),
                            reverse=True))
        count = 0
        while count < len(photosCommentedCount):
            tmpStr = (str(photosCommentedCount[count])+
                      "\t"+photosCommentedUser[count]+"\n")
            count += 1
            reportFile.write(tmpStr)


    reportFile.write("\n********** Analysis of time in Facebook **********\n")
    for timePost in timeOfPostList:
        tempList.append(timePost.split(" ")[1])
        tempTime = (timePost.split(" ")[1]).split(":")[0]
        tempTime = int(tempTime)
        if tempTime >= 21:
            timeSlot8+=1
        if tempTime >= 18 and tempTime < 21:
            timeSlot7+=1
        if tempTime >= 15 and tempTime < 18:
            timeSlot6+=1
        if tempTime >= 12 and tempTime < 15:
            timeSlot5+=1
        if tempTime >= 9 and tempTime < 12:
            timeSlot4+=1
        if tempTime >= 6 and tempTime < 9:
            timeSlot3+=1
        if tempTime >= 3 and tempTime < 6:
            timeSlot2+=1
        if tempTime >= 0 and tempTime < 3:
            timeSlot1+=1
    reportFile.write("Total % (00:00 to 03:00) "
                    +str((timeSlot1/totalLen)*100)+" %\n")
    reportFile.write("Total % (03:00 to 06:00) "
                    +str((timeSlot2/totalLen)*100)+" %\n")
    reportFile.write("Total % (06:00 to 09:00) "
                    +str((timeSlot3/totalLen)*100)+" %\n")
    reportFile.write("Total % (09:00 to 12:00) "
                    +str((timeSlot4/totalLen)*100)+" %\n")
    reportFile.write("Total % (12:00 to 15:00) "
                    +str((timeSlot5/totalLen)*100)+" %\n")
    reportFile.write("Total % (15:00 to 18:00) "
                    +str((timeSlot6/totalLen)*100)+" %\n")
    reportFile.write("Total % (18:00 to 21:00) "
                    +str((timeSlot7/totalLen)*100)+" %\n")
    reportFile.write("Total % (21:00 to 24:00) "
                    +str((timeSlot8/totalLen)*100)+" %\n")

    """
    reportFile.write("\nDate/Time of Facebook Posts\n")
    for timePost in timeOfPostList:
        reportFile.write(timePost+"\n")
    """
    reportFile.close()


def parseUserInfo(html):
    userEduWork     = []
    userLivingCity  = ""
    userCurrentCity = ""
    userLiveEvents  = []
    userGender      = ""
    userStatus      = ""
    userGroups      = []
    other           = []

    soup     = BeautifulSoup(html, "lxml")
    info     = soup.find_all("div", {"class" : "_50f3"})
    tempList = []

    for e in info:
        if   "Works"   in e.contents[0]:
            userEduWork.append(e.contents[1].contents[0])
        elif "Studied" in e.contents[0]:
            userEduWork.append(e.contents[1].contents[0])
        elif "Went"    in e.contents[0]:
            userEduWork.append(e.contents[1].contents[0])
        elif "Lives"   in e.contents[0]:
            userCurrentCity = e.contents[1].contents[0]
        elif "Single"  in e.contents[0] or "Married" in e.contents[0]:
            userStatus = e.contents[1].contents[0]
        elif "From"    in e.contents[0]:
            userLivingCity = e.contents[1].contents[0]
        elif "" in e.contents[0]:
            other.append(e.contents[1].contents[0])

#LiveEvents
#Gender
#Groups

    tempList.append([userEduWork,
                    userLivingCity,
                    userCurrentCity,
                    userLiveEvents,
                    userGender,
                    userStatus,
                    userGroups])
    return tempList


def parsePlaces(html):
    soup         = BeautifulSoup(html, "lxml")
    pageName     = soup.find_all("div", {"class" : "_2oqs clearfix"})
    pageCategory = soup.find_all("span", {"class" : " _c24"})
    tempList     = []
    count = 0
    r = re.compile('a href="(.*?)"')
    for x in pageName:
        m = r.search(str(x))
        if m:
            if len(pageCategory) > count:
                if pageCategory[count].contents:
                    categ = pageCategory[count].contents[0]
            name  = x.find("a").contents[0]
            url   = x.find("a")["href"]
            tempList.append([uid, name, categ, url])
            categ = "Other"
        count += 2
    return tempList


def parsePagesLiked(html):
    soup         = BeautifulSoup(html, "lxml")
    pageName     = soup.find_all("div", {"class" : "_52eh _5bcu"})
    pageCategory = soup.find_all("div", {"class" : "_pac"})
    tempList     = []
    r = re.compile('a href="(.*?)\?ref=')
    for i in range(len(pageCategory)):
        name  = pageName[2*i].find("span").contents[0]
        categ = pageCategory[i].find_all("span")[-1].contents[0]
        url   = pageName[2*i].find("a")["href"].split("?")[0]
        tempList.append([uid, name, categ, url])
    return tempList


def parsePhotos(html):
    soup          = BeautifulSoup(html, "lxml")
    tempList      = []
    pageName  = soup.find_all("img", {"class" : "scaledImageFitHeight img"})
    pageName1 = soup.find_all("img", {"class" : "scaledImageFitHeight img"})
    pageName2 = soup.find_all("img", {"class" : "_46-i img"})
    for z in pageName+pageName1+pageName2:
        if z["src"][:z["src"].index("?")].endswith(".jpg"):
            url1 = ("https://www.facebook.com/photo.php?fbid="
                    +str(z["src"]).split("_")[1]+"&set=bc")
            r    = re.compile("fbid=(.*?)&set=bc")
            m    = r.search(url1)
            if m:
                filename = "fbid_"+ m.group(1)+".html"
                filename = filename.replace("profile.php?id=","")
                if not os.path.lexists(filename):
                    html1 = downloadFile(url1)
                    print("[*] Caching Photo Page: ", m.group(1))
                    text_file = open(filename, "w")
                    text_file.write(str(html1))
                    text_file.close()
                else:
                    html1 = open(filename, "r").read()
            try:
                index     = str(html1).index("<a class=\"profileLink\"")
                username2 = str(html1)[index:index+100]
                username2 = username2.split("/")[3].split("?")[0]
            except ValueError:
                username2 = ""
                #print("Username not found")
                continue
            print("[*] Extracting Data from Photo Page: ", username2)
            tempList.append([str(uid),z["alt"],z["src"],url1,username2])
    return tempList


def parseVideosBy(html):
    soup       = BeautifulSoup(html, "lxml")
    videosURL  = soup.find_all("div", {"class" : "_4ou3"})
    videosName = soup.find_all("div", {"class" : "_4ovj"})
    tempList   = []
    for i in range(len(videosURL)):
        url   = "https://www.facebook.com"+videosURL[i].find("a")["href"]
        title = ""
        if videosName[i].contents:
            title = videosName[i].contents[0]
        tempList.append([uid, url, title])
    return tempList


def parseAppsUsed(html):
    soup = BeautifulSoup(html, "lxml")
    appsData = soup.find_all("div", {"class" : "_52eh _5bcu"})
    tempList = []
    for x in appsData:
        tempList.append(x.text)
    return tempList


def parseFriends(html):
    mthList = ["january","february","march","april","may","june","july",
               "august","september","october","november","december"]
    if len(html) > 0:
        soup = BeautifulSoup(html, "lxml")

        friendBlockData = soup.find_all("div",{"class" : "_3u1 _gli _uvb"})

        friendList=[]
        for i in friendBlockData:
            soup1 = BeautifulSoup(str(i), "lxml")
            friendNameData = soup1.find_all("div",{"class" : "_52eh _5bcu"})
            lastKnownData = soup1.find_all("div",{"class" : "_52eh"})
            r = re.compile("href=(.*?)\?ref")
            m = r.search(str(friendNameData))
            if m:
                try:
                    friendName = friendNameData[0].text
                    value = (lastKnownData[1].text).split("since")[1].strip()
                    #Current year - No year listed in page
                    if not re.search("\d+", value):
                        value = value+" "+str((datetime.now()).year)
                        month = ((re.sub(" \d+", " ", value)).lower()).strip()
                        monthDigit = 0
                        count=0
                        for s in mthList:
                            if s==month:
                                monthDigit=count+1
                            count+=1
                        year = re.findall("(\d+)",value)[0]
                        fbID = m.group(1).replace('"https://www.facebook.com/'
                                                 ,"")
                        friendList.append([str(uid),
                                           friendName,
                                           fbID,
                                           int(monthDigit),
                                           int(year)])
                    else:
                        #Not current year
                        month,year = value.split(" ")
                        month      = month.lower()
                        monthDigit = 0
                        count      = 0
                        for s in mthList:
                            if s == month:
                                monthDigit = count+1
                            count += 1
                        fbID = m.group(1).replace('"https://www.facebook.com/'
                                                 ,"")
                        friendList.append([str(uid),
                                           friendName,
                                           fbID,
                                           int(monthDigit),
                                           int(year)])


                except IndexError:
                    continue
                except AttributeError:
                    continue
        i=0
        data = sorted(friendList, key=operator.itemgetter(4,3))
        return data


def sidechannelFriends(uid):
    userList = []
    c = conn.cursor()
    c.execute("select distinct username from photosLiked where sourceUID=?"
             ,(uid,))
    dataList1 = []
    dataList1 = c.fetchall()
    if len(dataList1) > 0:
        for i in dataList1:
            if "pages" not in str(i[0]):
                userList.append([uid,"",str(i[0]),"",""])
    c.execute("select distinct username from photosCommented where sourceUID=?"
             ,(uid,))
    dataList1 = []
    dataList1 = c.fetchall()
    if len(dataList1) > 0:
        for i in dataList1:
            if "pages" not in str(i[0]):
                userList.append([uid,"",str(i[0]),"",""])
    c.execute("select distinct username from photosOf where sourceUID=?"
             ,(uid,))
    dataList1 = []
    dataList1 = c.fetchall()
    if len(dataList1) > 0:
        for i in dataList1:
            if "pages" not in str(i[0]):
                userList.append([uid,"",str(i[0]),"",""])
    return userList


def getFriends(uid):
    userList = []
    c = conn.cursor()
    c.execute("select username from friends where sourceUID=?",(uid,))
    dataList1 = []
    dataList1 = c.fetchall()
    if len(dataList1) > 0:
        for i in dataList1:
            userList.append([uid,"",str(i),"",""])
    return userList


def mainProcess(username):
    username = username.strip()
    print("[*] Username:\t", str(username))
    global uid

    loginFacebook(driver)
    uid = convertUser2ID(driver,username)
    if not uid:
        print("[!] Problem converting username to uid")
        sys.exit()
    else:
        print("[*] Uid:\t", str(uid))

    filename = username+"_apps.html"
    html     = download(filename, "apps-used", username)
    dataList = parseAppsUsed(html)
    result   = ""
    for x in dataList:
        x = x.lower()
        if "blackberry" in x:
            result += "[*] User is using a Blackberry device\n"
        if "android" in x:
            result += "[*] User is using an Android device\n"
        if "ios" in x or "ipad" in x or "iphone" in x:
            result += "[*] User is using an iOS Apple device\n"
        if "samsung" in x:
            result += "[*] User is using a Samsung Android device\n"
    print(result)

    filename = username+"_pages.html"
    html     = download(filename, "pages-liked", username)
    dataList = parsePagesLiked(html)
    if len(dataList) > 0:
        write2Database("pagesLiked",dataList)

    filename = username+"_videosBy.html"
    html     = download(filename, "videos-by", username)
    dataList = parseVideosBy(html)
    if len(dataList) > 0:
        write2Database("videosBy",dataList)

    filename = username+"_photosOf.html"
    html     = download(filename, "photos-of", username)
    dataList = parsePhotos(html)
    if len(dataList) > 0:
        write2Database("photosOf",dataList)

    filename = username+"_photosBy.html"
    html     = download(filename, "photos-by", username)
    dataList = parsePhotos(html)
    if len(dataList) > 0:
        write2Database("photosBy",dataList)

    filename = username+"_photosLiked.html"
    html     = download(filename, "photos-liked", username)
    dataList = parsePhotos(html)
    if len(dataList) > 0:
        write2Database("photosLiked",dataList)

    filename = username+"_photoscommented.html"
    html     = download(filename, "photos-commented", username)
    dataList = parsePhotos(html)
    if len(dataList) > 0:
        write2Database("photosCommented",dataList)

    filename = username+"_friends.html"
    html     = download(filename, "friends", username)
    if len(html.strip()) > 1:
        dataList = parseFriends(html)
        print("[*] Writing friends list to database: ", username)
        write2Database("friends",dataList)
    else:
        print("[*] Extracting friends from likes/comments: ", username)
        write2Database("friends",sidechannelFriends(uid))

    c = conn.cursor()
    c.execute("select * from friends where sourceUID=?",(uid,))
    dataList = c.fetchall()
    photosliked     = []
    photoscommented = []
    userID          = []
    for i in dataList:
        c.execute("select * from photosLiked where sourceUID=? and "
                  "username=?",(uid,i[2],))
        dataList1 = []
        dataList1 = c.fetchall()
        if len(dataList1) > 0:
            str1 = ([dataList1[0][4],str(len(dataList1))])
            photosliked.append(str1)

        c.execute("select * from photosCommented "
                        "where sourceUID=? and username=?",(uid,i[2],))
        dataList1 = []
        dataList1 = c.fetchall()
        if len(dataList1) > 0:
            str1 = ([dataList1[0][4],str(len(dataList1))])
            photoscommented.append(str1)

    filename = username+".html"
    html     = download(filename, "timeline", username)
    parseTimeline(html,username)
    writeReport(username)

    print("\n")
    print("[*] Downloading user information")

    tmpInfoStr = []
    userID = getFriends(uid)
    for x in userID:
        i = str(x[2])
        i = i.replace("('","").replace("',","").replace(")","")
        i = i.replace('"https://www.facebook.com/',"")
        print("[*] Looking up information on ", i)
        filename = i+".html"
        if "/" not in filename:
            if not os.path.lexists(filename):
                print("Writing to ", filename)
                url  = "https://www.facebook.com/"+i+"/info"
                html = downloadFile(url)
                if len(html) > 0:
                    text_file = open(filename, "w")
                    text_file.write(html)
                    text_file.close()
            else:
                print("Skipping: ", filename)
            print("[*] Parsing user information: ", i)
            html         = open(filename, "r").read()
            userInfoList = parseUserInfo(html)[0]
            tmpStr       = []
            tmpStr.append([uid,str(i),
                            str(userInfoList[0]),
                            str(userInfoList[1]),
                            str(userInfoList[2]),
                            str(userInfoList[3]),
                            str(userInfoList[4]),
                            str(userInfoList[5]),
                            str(userInfoList[6])])
            try:
                write2Database("friendsDetails",tmpStr)
            except:
                continue

    cprint("[*] Report has been written to: "+str(reportFileName),"white")
    cprint("[*] Preparing Maltego output...","white")
    createMaltego(username)
    cprint("[*] Maltego file has been created","white")


def options(arguments):
    user  = ""
    count = 0
    for arg in arguments:
        if arg == "-user":
            count += 1
            user   = arguments[count+1]
        elif arg == "-report":
            count += 1
            global reportFileName
            reportFileName = arguments[count+1]
    mainProcess(user)


def showhelp():
    print("Usage: python fb.py -user [Facebook Username] -report "
          "[Filename of report]")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        showhelp()
        driver.close()
        driver.quit
        conn.close()
        sys.exit()
    else:
        if len(facebook_username) < 1 or len(facebook_password) < 1:
            print("[*] Please fill in 'facebook_username' and "
                  "'facebook_password' before continuing.")
            sys.exit()
        options(sys.argv)

