# (c) 2007 by d0k
# Licensed under GPLv2

from os import path
import string
from urlparse import urlsplit
import xml.dom.minidom

class Metalinkfile:
	def __init__(self, metalink, distributor, filepath):
		self.__metalink = metalink
		metalink.mirrorlist.seek(0)
		for line in metalink.mirrorlist:
			mirrors = string.split(line)
			if mirrors[0] == distributor:
				break
		else:
			raise Exception('distributor %s not found.'%distributor)
		del mirrors[0]
	
		self.file = metalink.doc.createElement('file')
		self.file.setAttribute('name', path.basename(filepath))
		resources = metalink.doc.createElement('resources')

		for mirror in mirrors:
			url = metalink.doc.createElement('url')
			mirrorurl = urlsplit(mirror)
			url.setAttribute('type', mirrorurl.scheme)
			if metalink.gi:
				country = metalink.gi.country_code_by_name(mirrorurl.hostname)
				if country:
					url.setAttribute('location', country.lower())
			url.appendChild(metalink.doc.createTextNode(mirror+'/'+filepath))
			resources.appendChild(url)

		self.file.appendChild(resources)
		metalink.files.appendChild(self.file)

		self.ver = False

	def __checkver(self):
		if not self.ver:
			self.ver = self.__metalink.doc.createElement('verification')
			self.file.appendChild(self.ver)

	def __createHashNode(self, hashtype, hashvalue):
		self.__checkver()
		hash = self.__metalink.doc.createElement('hash')
		hash.setAttribute('type', hashtype)
		hash.appendChild(self.__metalink.doc.createTextNode(hashvalue))
		self.ver.appendChild(hash)

	def __createSigNode(self, contents):
		self.__checkver()
		sig = self.__metalink.doc.createElement('signature')
		sig.setAttribute('type', 'pgp')
		sig.appendChild(self.__metalink.doc.createTextNode('\n'+contents))
		self.ver.appendChild(sig)

	def addmd5hash(self, hash):		
		if len(hash) == 32:
			self.__createHashNode('md5', hash)
		else:
			raise Exception('Invalid MD5 sum')

	def addsha1hash(self, hash):
		if len(hash) == 40:
			self.__createHashNode('sha1', hash)
		else:
			raise Exception('Invalid SHA1 sum')

	def addsigfile(self, file):
		f = open(file)
		self.__createSigNode(f.read())
		f.close()
