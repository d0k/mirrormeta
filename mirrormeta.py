#!/usr/bin/env python
#
# (c) 2007 by d0k
# Licensed under GPLv2
# Uses thirdpartymirrors list from Gentoo Linux (http://gentoo.org/)

from optparse import OptionParser
from os import path
import string
import sys
from urlparse import urlsplit
import xml.dom.minidom

parser = OptionParser(usage='usage: %prog [options] distributor file\n\te.g. %prog -g sourceforge testproject/test.tar.gz')
parser.add_option("-o", action="store", type="string", metavar="FILE", dest="filename", help="output file (default: stdout)")
parser.add_option("-m", action="store", type="string", metavar="FILE", dest="mirrorlist", default="thirdpartymirrors", help="mirror list to use (default: thirdpartymirrors)")
parser.add_option("-g", action="store_true", dest="hasgeoip", default=False, help="use geoip lookup (if available)")
(options, args) = parser.parse_args()

if len(args) != 2:
	parser.print_help()
	sys.exit(1)

if options.hasgeoip:
	try:
		import GeoIP
		gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
	except ImportError:
		sys.exit('GeoIP or GeoIP-python not found!')

if options.filename:
	output = open(options.filename, 'w')
else:
	output = sys.stdout

f = open(options.mirrorlist)
for line in f:
	mirrors = string.split(line)
	if mirrors[0] == args[0]:
		break
else:
	sys.exit('distributor %s not found.'%args[0])
f.close()
del mirrors[0]

doc = xml.dom.minidom.Document()
metalink = doc.createElementNS('http://www.metalinker.org/', 'metalink')
metalink.setAttribute('xmlns', 'http://www.metalinker.org/') # TODO: force xmlns in a nicer fashion 
metalink.setAttribute('version', '3.0')
doc.appendChild(metalink)

files = doc.createElement('files')
file = doc.createElement('file')
file.setAttribute('name', path.basename(args[1]))
resources = doc.createElement('resources')

for mirror in mirrors:
	url = doc.createElement('url')
	mirrorurl = urlsplit(mirror)
	url.setAttribute('type', mirrorurl.scheme)
	if options.hasgeoip:
		country = gi.country_code_by_name(mirrorurl.hostname)
		if country:
			url.setAttribute('location', country.lower())
	url.appendChild(doc.createTextNode(mirror+'/'+args[1]))
	resources.appendChild(url)

file.appendChild(resources)
files.appendChild(file)
metalink.appendChild(files)

output.write(doc.toxml())
output.write('\n')
