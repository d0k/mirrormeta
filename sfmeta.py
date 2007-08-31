#!/usr/bin/env python
# (c) 2007 by d0k
# Licensed under GPLv2
# generates metalink files from sf.net URLs
# Uses thirdpartymirrors list from Gentoo Linux (http://gentoo.org/)

from optparse import OptionParser
import sys
from urlparse import urlsplit
from mirrormeta import *

parser = OptionParser(usage='usage: %prog [options] sf.net URL [sf.net URL] [...]')
parser.add_option("-o", action="store", type="string", metavar="FILE", dest="filename", help="output file (default: stdout)")
parser.add_option("-m", action="store", type="string", metavar="FILE", dest="mirrorlist", default="thirdpartymirrors", help="mirror list to use (default: thirdpartymirrors)")
#parser.add_option("--md5", action="store", type="string", metavar="SUM", dest="md5sum", help="embed SUM as md5 sum")
#parser.add_option("--sha1", action="store", type="string", metavar="SUM", dest="sha1sum", help="embed SUM as sha1 sum")
#parser.add_option("--sig", action="store", type="string", metavar="FILE", dest="sigfile", help="embed contents of FILE as gpg signature")
(options, args) = parser.parse_args()

if len(args) == 0:
	parser.print_help()
	sys.exit(1)

if options.filename:
	output = open(options.filename, 'w')
else:
	output = sys.stdout

mirrorlist = open(options.mirrorlist)
meta = Metalink(mirrorlist, True)

for arg in args:
	url = urlsplit(arg)
	file = Metalinkfile(meta, 'sourceforge', url.path[1:])

	#if options.md5sum:
	#	file.addmd5hash(options.md5sum)
	#
	#if options.sha1sum:
	#	file.addsha1hash(options.sha1sum)
	#
	#if options.sigfile:
	#	file.addsigfile(options.sigfile)

output.write(meta.toxml())
output.write('\n')
