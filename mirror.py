#!/usr/bin/env python
#
# (c) 2007 by d0k
# Licensed under GPLv2
# Uses thirdpartymirrors list from Gentoo Linux (http://gentoo.org/)

import sys, string
from os import path
import xml.dom.minidom

if len(sys.argv) == 3:
	output = sys.stdout
elif len(sys.argv) == 4:
	output = open(sys.argv[3], 'w')
else:
	sys.stderr.write('mirrormeta.py distributor file [output]\n')
	sys.exit(1)

f = open('thirdpartymirrors', 'r')
for line in f:
	mirrors = string.split(line)
	if mirrors[0] == sys.argv[1]:
		break
else:
	sys.stderr.write('%s not found.\n'%sys.argv[1])
	sys.exit(1)
f.close()
del mirrors[0]

doc = xml.dom.minidom.Document()
metalink = doc.createElementNS('http://www.metalinker.org/', 'metalink')
metalink.setAttribute('xmlns', 'http://www.metalinker.org/')
metalink.setAttribute('version', '3.0')
doc.appendChild(metalink)

files = doc.createElement('files')
file = doc.createElement('file')
file.setAttribute('name', path.basename(sys.argv[2]))
resources = doc.createElement('resources')
for mirror in mirrors:
	url = doc.createElement('url')
	url.setAttribute('type', string.split(mirror, '://')[0])
	url.appendChild(doc.createTextNode(mirror+'/'+sys.argv[2]))
	resources.appendChild(url)
file.appendChild(resources)
files.appendChild(file)
metalink.appendChild(files)

output.write(doc.toxml())
