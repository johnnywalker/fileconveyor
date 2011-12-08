File Conveyor
=============

Introduction
------------

The following intro was written by the original author, Wim Leers:

> File Conveyor is a daemon written in Python to detect, process and sync files. 
> In particular, it's designed to sync files to CDNs. Amazon S3 and Rackspace 
> Cloud Files, as well as any Origin Pull or FTP Push CDN, are supported. 
> Originally written for my bachelor thesis at Hasselt University in Belgium.

> [http://www.fileconveyor.org](http://www.fileconveyor.org)

This Fork
---------

I was looking for something that had the event driven design of File Conveyor
but provided an OS X interface. Some modifications were made to the original
source, but primarily I just added a user interface in the form of a "menu bar
extra", officially termed a NSStatusBar menu. This application does not consume
any space in the dock, but instead places an icon in the menu bar, allowing you
to start/stop the daemon and view its output. The configuration and database
files are placed in "~/Library/Application Support/FileConveyor".

Note: There is no configuration interface, and the integration with the original
daemon is minimally buttered - just enough to be useful. At the moment, I have
no immediate plans to improve the aforementioned, but it's hard to tell the
future.

*Johnny Walker*

Installation
------------

To create an app bundle from the sources, just enter `python setup.py py2app`.
