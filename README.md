HumbleBundle backup
===================

### Description

I made this piece of code for myself, so I could backup my
HumbleBundle library on my machine. Perhaps other people,
who want to do the same, can profit from this work.
It is kept very simple, because once it did the job for me
I stopped working on it.

### Usage

Enter the content of your authentication cookie ("_simpleauth_sess"
from humblebundle.com) you got from logging in via a  Webbrowser
in the auth string below. Enter a target directory as well.
The script will now download all BumbleBundle files currently accessible
via the HumbleBundle API, which is undocumented for the public.

It is not able to download alterative versions of the same content,
for example if there is a mp3 and FLAC Soundtrack or there are multiple
Linux package formats it will only download the first in the list.

You can check which files are still missing in you target directory,
for example for downloading the missing files manually, by passing "--list-missing-files-only" as a commandline argument.
You can also speed the process up by disabling the check for correct local filesizes for redownloading files in case of wrong filesize by passing "--no-filesize-check".

Have fun!

**If anybody has an idea on how to use the HumbleBundle API so I can really download *all* files, I would be happy to learn it and improve this script accordingly.**
