#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
             --- humblebundle-backup by guitargeek ---

Description: I made this piece of code for myself, so I could backup my
             humblebundle library on my machine. Perhaps other people,
             who want to do the same, can profit from this work.
             It is kept very simple, because once it did the job for me
             I stopped working on it.

Usage: enter the content of your authentication cookie ("_simpleauth_sess"
       from humblebundle.com) you got from logging in via a  Webbrowser
       in the auth string below. Enter a target directory as well.
       The script will now download all humblebundle-files accessible
       via the officialy undocumented humblebundle API.

       It is not able to download alterative versions of the same content,
       for example if there is a mp3 and FLAC Soundtrack or there are multiple
       Linux package formats it will only download the first in the list.

       You can check which files are still missing in you target directory
       by passing "--list-missing-only" as a commandline argument. You can
       also speed the process up by disabling the check for correct local
       filesizes for redownloading stuff in case of wrong filesize by passing
       "--no-filesize-check".

       Have fun!
"""

"""
Edit this
"""
# The content of the auth-cookie should be a huge string with random letters and numbers.
auth = ""
# Insert you target directory of choice. Multiple subfolders corresponding
# to the different Games will be created in the target directory.
target_dir = ""

"""
Now the real program starts
"""

import requests, cookielib, os, sys, json, urllib2
from urlparse import urljoin, urlsplit

URL = "https://www.humblebundle.com"
LOGIN_URL = 'https://www.humblebundle.com/login'
ORDER_LIST_URL = 'https://www.humblebundle.com/api/v1/user/order'
ORDER_URL = 'https://www.humblebundle.com/api/v1/order/{order_id}'
CLAIMED_ENTITIES_URL = 'https://www.humblebundle.com/api/v1/user/claimed/entities'
SIGNED_DOWNLOAD_URL = 'https://www.humblebundle.com/api/v1/user/Download/{0}/sign'
STORE_URL = 'https://www.humblebundle.com/store/api/humblebundle'

def download_file(opened_url, file_size, target_file_name):
    f = open(target_file_name, 'wb')
    print u"Downloading: {0}, Size: {1:.1f} MB.".format(target_file_name, file_size / 1024.0**2)
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

if auth == "" or auth == None:
    print "Authentication cookie content missing!"
    sys.exit()

if target_dir == None:
    print "Target dir unspecified!"
    sys.exit()

list_missing_only = "--list-missing-only" in sys.argv
no_filesize_check = "--no-filesize-check" in sys.argv

if target_dir != "" and target_dir[-1] != "/":
    target_dir = target_dir + "/"

# Create a cookiejar with the authentication cookie inside
cookiejar = cookielib.MozillaCookieJar()
expires = int(auth.split('|')[1]) + 730 * 24 * 60 * 60
cookie = cookielib.Cookie(version = 0, name = '_simpleauth_sess', value = auth,
          port = None, port_specified = False, domain = urlsplit(URL)[1],
          domain_specified = False, domain_initial_dot = False, path = '/',
          path_specified = False, secure = True, expires = expires,
          discard = False, comment = None, comment_url = None, rest={},)
cookiejar.set_cookie(cookie)

print "Get list with all claimed entities from humblebundle.com..."
r = requests.get(CLAIMED_ENTITIES_URL, cookies=cookiejar)
data = json.loads(r.text.replace("\u00fc", "u"))

target_folder_dict = {}

if not list_missing_only:
    print "Calculating total library size.."
    total_size = 0
    for item in data["Downloads"]:
        machine_name = item["machine_name"]
        for download in item["download_struct"]:
            if "file_size" in download.keys():
                total_size = total_size + download["file_size"]

    proceed = raw_input("Total library size will be {0:.2f} GB. Continue? [y/n]: ".format(total_size / 1024.0**3))
    while proceed.lower() != "y":
        if proceed.lower() == "n":
            sys.exit()
        proceed = raw_input("Thats not a valid option. Continue? [y/n]: ")

print "Updating directory structure..."
for item in data["SubProducts"]:
    human_name = item["human_name"]
    # Creating a directory with the human readable name, if it does not extist
    if not os.path.exists(target_dir + human_name):
        os.makedirs(target_dir + human_name)
    for machine_name in item["_filtered_download_machine_names"]:
        target_folder_dict[machine_name] = human_name

if not list_missing_only:
    for item in data["SubProducts"]:
        human_name = item["human_name"]
        # Unfortunately, there is not a machine name for every download to generate
        # a signed URL. Downloads with more than one flavor (mp3, FLAC) will only
        # download the first in the download_struct dictionary.
        # See entities file for understanding this problem.
        # Machine names with the "_asm" ending (Browsergames) are excluded.
        for machine_name in [i for i in item["_filtered_download_machine_names"] if not i.endswith("_asm")]:
            file_name = target_dir + human_name + "/" + [i for i in data["Downloads"] if i["machine_name"] == machine_name][0]["download_struct"][0]["url"]["web"]
            if os.path.isfile(file_name):
                if no_filesize_check:
                    print chr(8) + "File {0} already exists.".format(file_name)
                    break
                else:
                    local_file_size = os.path.getsize(file_name)
            else:
                local_file_size = 0
            r = requests.get(SIGNED_DOWNLOAD_URL.format(machine_name), cookies=cookiejar)
            url = json.loads(r.text)["signed_url"]
            u = urllib2.urlopen(url)
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            # Check if the file already exists and has the right size
            if local_file_size != file_size:
                download_file(u, file_size, file_name)
            else:
                print chr(8) + u"File {0} already exists and has correct size.".format(file_name)

    print "All downloads complete!"

# Lastly, check which files were missed due to strange humblebundle API
print "Files which are still missing in the local library:"
for x in data["Downloads"]:
    for download in x["download_struct"]:
        if "url" in download.keys():
            file_name = target_dir + target_folder_dict[x["machine_name"]] + "/" + download["url"]["web"]
            if not os.path.isfile(file_name):
                print " - " + "/".join(file_name.split("/")[-2:])
