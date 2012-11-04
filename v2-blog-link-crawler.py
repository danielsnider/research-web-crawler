#!/usr/bin/python
# 
# Copyright 2010 Daniel Snider
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import HTMLParser
import threading
import urllib
import csv
import os
import sys
import thread
import time
import getopt

## @mainpage Blog Link Crawler
# This program crawls web pages and keeps track of hyperlinks. Main class is Node.
#
# @brief --->Node<---
# @author Daniel Snider 
# @date 2010
# @note work in progress
# @note most functions work best when the root node is the object in question
#
# Global Variables:
#
# crawled_sites = list of unique crawled sites. I have no idea if this is efficient but it is very required. This is used to ensure a site is not crawled twice. This is also used for the rows of the adjacency matrix.
#
# unique_sites = numebr of unique sites is usually different than the number of crawled sites because not all collected sites have been crawled. This is used as the columns of the adjacency matrix.
#
#blacklist = sites that should be ignored. There are a bunch of pesky wordpress sites that I need to block. 
#@todo create a root global variable to reduce confusion of what object should be called

crawled_sites = [] 
unique_sites = [] 
blacklist = []
save_data_frequency = 300 #interval in seconds that the data is saved

##Saves the tree periodically
def saveData():
	for i in range(99999):
		time.sleep(save_data_frequency)
		#root.exportMatrix()
		root.exportMultiLineMatrix()
		root.exportCrawled_sites()
		root.exportUnique_sites()	

class parseLinks(HTMLParser.HTMLParser): 
	## @class parseLinks
	#
	#This class is for parsing html pages
	
	##The constructor
	def __init__(self, node): #this function is copy pasted from http://pleac.sourceforge.net/pleac_python/webautomation.html
		HTMLParser.HTMLParser.__init__(self)
		self._plaintext = "" #dont know what this is
		self._ignore = False #dont know what this is
		self.node = node 
		## @var node
		#I added this so that when crawling is happening and a new site is found, the node object being crawled can be accessed and the new site can be added in the approriate place
	
	## This function parses the tags of the website and creates new nodes for each site found.
	# The code was found from page 170 of Python Phrasebook
	#@todo add "typepad" to the list of accepable domains
	def handle_starttag(self, tag, attrs): 
		global blacklist
		banfound = False
		if tag == 'a': 
			for name, value in attrs:
				if name == 'href':
					if (value.find("http://")+1):
						if (value.find("wordpress") >= 0) or (value.find("blogspot") >= 0): #add typepad here
							#print self.node.site + " ---> " + value
							for site in blacklist:
								if value.find(site) >= 0:
									banfound = True
							if banfound == False: #if the site is not in the banned list
								self.node.insert(value) #create new node


## @author Daniel Snider
class Node:
	## @class node
	#This class is a graph data structure and is used to build a graph of links between websites. 

	##The constructor
	#@brief When a new node is created the links array is set to empty and the website string is set to be the newsite string that was passed in.
	#@param self The object pointer.
	#@param newsite The string URL of the new website.
	#@retval None
	def __init__(self, newsite):
		self.links = [] 
		## @var links
		# A list of nodes. Each node represents a website.
		self.site = newsite
		## @var site
		#Contains the website as a string.
		
	##Inserts a site into the connection graph. Inserts the site into the links[] array for the current (self) site
	#@brief Also checks for duplicates. i.e. won't crawl if the input site has already been crawled
	#@param self The object pointer.
	#@param newsite The string URL of the new website.
	#@retval None
	def insert(self, newsite):
		if self.dupCheck(newsite): #disallows duplicates in a node's "links" list. and disallows the new site to be it's self
			n = Node(newsite)
			self.links.append(n)
			global unique_sites
			add = True
			for site in unique_sites:
				if site.site.find(newsite) >= 0:
					add = False
			if add == True:		
				unique_sites.append(n)

	##Downloads a webpage and collects hyperlinks
	#@brief Also checks for duplicates.
	#@note HTMLParser is used and is very strict, probably too strict and we are missing some sites. Documentation on this: http://www.python-forum.org/pythonforum/viewtopic.php?f=19&t=9348
	#@param self The object pointer.
	#@param nu,ll Useless variables. Once needed for attempting to multithread.
	#@retval None
	#@todo remove useless variables nu and ll.
	def crawl(self, nu,ll):
		global crawled_sites	
		alreadycrawled = False
		for site in crawled_sites:
			if self.site == site.site : #check to ensure a site is not crawled twice
				alreadycrawled = True

		if not alreadycrawled:
			crawled_sites.append(self)			
			#page 170 of Python Phrasebook:
			lParser = parseLinks(self)
			try:
				s = urllib.urlopen(self.site).read()
				lParser.feed(s); 
				lParser.close()
			except Exception: pass
			#except HTMLParser.HTMLParseError, msg:	pass#HTMLParser is very strict, probably too strict and we are missing some sites http://www.python-forum.org/pythonforum/viewtopic.php?f=19&t=9348
			#except IOError: print "IOErrer on: ", self.site
			#except UnicodeDecodeError: print "UnicodeDecodeError on: ", self.site
			#except httplib.InvalidURL: pass #this exception is not right, it is a syntax error

	##Crawls every link in a node's links
	#@brief Prints a "." for each site that is crawled
	#@param self The object pointer.
	#@retval None
	#@todo multithread
	def walkCrawl(self):
		if (self.links == []):
			sys.stdout.write('.')
			sys.stdout.flush()
			#print thread.start_new_thread(self.crawl, (0, 0))
			self.crawl(0,0)
		else:
			for link in self.links:
				link.walkCrawl()
	
	##Prints every node
	#@brief Prints to console each site and the site that linked to it in the form: www.Parent site --> www.Child site
	#@param self The object pointer.
	#@param root Parent site so to keep track of who the parent is for more informative print
	#@retval None
	def walkPrint(self, root):
		if (self.links == []):
			print root.site + " --> " + self.site
		else:
			for link in self.links:
				link.walkPrint(self)

	##Special formating used to export sites to .csv.
	#@brief 
	#@param self The object pointer.
	#@retval str Returns all the links that are linked by a site in one string
	def cat_links(self):
		if (self.links == []):
			return ''
		else:
			s = ""
			for link in self.links:
				s = s + link.site + " "
			return s
	
	##Counts the number of nodes
	#@param self The object pointer.
	#@retval int The number of node objects in the graph.
	def count(self):
		if (self.links == []):
			return 0
		else:
			i = 0 #NOTE THIS DOES NOT count first node
			for link in self.links:
				i = i + link.count() + 1 #account for each node
			return i

	##Checks if a website is already linked by a site. i.e. disallows duplicates in a node's "links" list. and disallows the new site to be it's self
	#@param self The object pointer.
	#@param newsite The string URL of the new website.
	#@retval bool true if website is not already present, false if website is already present
	#@todo instead of taking just the first link to a domain found, we could possibly always use the plain domain
	#@todo when determining the damain of a full URL change algorithm to determine the end of the domain with ".com" or ".net" and a "/". every domain seems to follow the rule of ".something/" for tho root of the site, i.e. the domain. 
	def dupCheck(self, newsite):
		if (self.links == []): #if links is empty there could obviously not be a dupliate
			return True
		else:
			#here I have to trim the url so that it is just comparing the newmsites domain. we care about the social network more than individual sites. thats why we only need one site from each damain. in this case the first link is the only link taken. also it only works for .coms and .net sites, others can get threw. we could
			trimlength = newsite.find(".com") #if new site is a .com site
			if (trimlength < 0): 
				trimlength = newsite.find(".net") #or a .net site
				if (trimlength < 0):
					return True
			trimmedsite = ""
			for char in range(trimlength):
				trimmedsite  = trimmedsite + newsite[char] #for each character between the start of the newsite to the .com or .net append it to a newvariable. end result is the trimmedsite variable will be just the domain of the newsite
			if (self.site.find(trimmedsite)+1): return False #campare domain of the newsite to the site being crawled
			for link in self.links: #campare domain of the newsite to all the links that the site bieng crawled has so to not allow deplicates.
				if (link.site.find(trimmedsite)+1): return False
			return True

	##Creates a spreadsheet of the graph
	#@brief [DEPRECIATED] Creates the file links.csv. It is a spreadsheet. Each row will contain the list of sites linked by a site.
	#@param self The object pointer. Should be the root node if you want the whole graph created
	#@retval None
	#@todo each row should begin with the parent site but does not currently I don't believe. Piority: low
	#@bug breaks when nuber of nodes gets over like 30
	def export_csv(self):
		filename = "links.csv"
		f = open(filename, "w")
						
		def recursive_write(site):
			basecase = True	
			for link in site.links:
				if not(link.links == []): 
					basecase = False
			if basecase: 
				print >>f, site.cat_links()			
			else:
				for link in site.links:
					recursive_write(site)
				print >>f, site.cat_links()
				
		recursive_write(self)
		f.close()
	
	##Prints an adjecency matrix to console
	#@brief Prints out 1s and 0s in a grid with each unique site on the horizontal and vertical and where a website intersects with a website that it links the to, the link is represented by 1. The matrix should be read horizontally
	#@param self The object pointer. Should be the root node if you want the whole graph created
	#@retval None
	#@todo check logic. Priority: low
	def printMatrix(self):
		global unique_sites
		for site in unique_sites:
			if site in self.links:
				sys.stdout.write("1 ")
			else:	
				sys.stdout.write("0 ")
		sys.stdout.write("\n")
		sys.stdout.flush()
		for link in self.links:
			if not link.links == []:
				link.printMatrix()
	
	##Creates a file containing an adjacency matrix in Matlab format. The adjacency matrix has a row for each crawled site and a column for each unique site found (which includes crawled sites and child nodes, i.e. non-crawled sites).
	#@param self The object pointer. Should be the root node if you want the whole graph created
	#@retval None
	#@todo check logic. Priority: high
	def exportMatrix(self):
#		global unique_sites
		filename = "mat_matrix"
		f = open(filename, "w")
				
		f.write("% Created by Daniel Snider's WebLinkCrawler v1.0 ")
		f.write(str(time.ctime()))
		f.write("\n% starting site: ")
		f.write(self.site)
		f.write("\n% crawled sites: ")
		f.write(str(len(crawled_sites)))
		f.write("\n% connections: ")
		f.write(str(root.count()))
		f.write("\n% sites: ")
		f.write(str(len(unique_sites)))
		f.write("\nm = [")
						
		def write(s):
			for site in unique_sites: #each column will be a unique site
				found = False
				for link in s.links:
					if site.site == link.site:
						found = True
				if found == True:
					f.write(" 1")
				else:	
					f.write(" 0")
			f.write(";")
			
		for site in unique_sites: #each unique site will be a row
				write(site)		
		f.write("];")
		f.close()
		
	def exportMultiLineMatrix(self):
		filename = "matrix"
		f = open(filename, "w")
				
		f.write("% Created by Daniel Snider's WebLinkCrawler v1.0 ")
		f.write(str(time.ctime()))
		f.write("\n% starting site: ")
		f.write(self.site)
		f.write("\n% crawled sites: ")
		f.write(str(len(crawled_sites)))
		f.write("\n% connections: ")
		f.write(str(root.count()))
		f.write("\n% sites: ")
		f.write(str(len(unique_sites)))
		f.write("\n")
						
		def write(s):
			for site in unique_sites: #each column will be a unique site
				found = False
				for link in s.links:
					if site.site == link.site:
						found = True
				if found == True:
					f.write(" 1")
				else:	
					f.write(" 0")
			f.write("\n")
			
		for site in unique_sites: #each unique site will be a row
				write(site)		
		f.close()
	
	def exportCrawled_sites(self):
		global unique_sites
		filename = "crawled"
		f = open(filename, "w")
				
		f.write("% Created by Daniel Snider's WebLinkCrawler v1.0 ")
		f.write(str(time.ctime()))
		f.write("\n% starting site: ")
		f.write(self.site)
		f.write("\n% crawled sites: ")
		f.write(str(len(crawled_sites)))
		f.write("\n% connections: ")
		f.write(str(root.count()))
		f.write("\n% sites: ")
		f.write(str(len(unique_sites)))

		for site in crawled_sites:
			f.write("\n")
			f.write(site.site)
		
	def exportUnique_sites(self):
		global unique_sites
		filename = "unique"
		f = open(filename, "w")
				
		f.write("% Created by Daniel Snider's WebLinkCrawler v1.0 ")
		f.write(str(time.ctime()))
		f.write("\n% starting site: ")
		f.write(self.site)
		f.write("\n% crawled sites: ")
		f.write(str(len(crawled_sites)))
		f.write("\n% connections: ")
		f.write(str(root.count()))
		f.write("\n% sites: ")
		f.write(str(len(unique_sites)))

		for site in unique_sites:
			f.write("\n")
			f.write(site.site)

#--------------------------------------------

d = 5

try:
	opts, args = getopt.getopt(sys.argv[1:], 'd' ,['depth'])
	for opt, arg in opts:
		if (opt == "--depth") | (opt == "-d"):
			d = args[0] #set depth of crawl, i.e length of loop

except getopt.GetoptError:
	print "usage:"
	print "  -d, --depth [number] \tsets depth of crawl".expandtabs(25)
	print "  -h, --help \tprints this help".expandtabs(25)
	sys.exit(0)

blacklist.append("http://wordpress.com/")
blacklist.append("http://wordpress.com/wp-login.php?action=lostpassword")
blacklist.append("http://en.support.wordpress.com/")
blacklist.append("http://vip.wordpress.com/")
blacklist.append("http://iphone.wordpress.org/")
blacklist.append("http://en.forums.wordpress.com/")
blacklist.append("http://en.wordpress.com/features/")
blacklist.append("http://blackberry.wordpress.org/")
blacklist.append("http://android.wordpress.org/")
blacklist.append("http://support.wordpress.com/apps/")
blacklist.append("http://wordpress.org/")
blacklist.append("http://wordpress.tv/")
blacklist.append("http://en.blog.wordpress.com/")
blacklist.append("http://en.wordpress.com/tag/")
blacklist.append("http://en.wordpress.com/signup/?ref=navigation")
blacklist.append("http://2chan.us/")
blacklist.append("http://1.bp.blogspot.com/")
blacklist.append("http://2.bp.blogspot.com/")
blacklist.append("http://3.bp.blogspot.com/")
blacklist.append("http://4.bp.blogspot.com/")
blacklist.append(".files.wordpress.com")
#blacklist.append("")

root = Node("http://awkwardprops.blogspot.com/") #other possible site: http://type-01.blogspot.com/ http://terrymcdaniel.wordpress.com/ http://aliceandcamilla.blogspot.com/ http://electricgoldfish.blogspot.com/?expref=next-blog

unique_sites.append(root)
#http://rgbvalues.blogspot.com/
print str(time.ctime())

t = threading.Thread(target=saveData)
t.start()

for i in range(int(d)):
	root.walkCrawl()
	sys.stdout.write(str(i+1))
	sys.stdout.write("=")
	sys.stdout.write(str(root.count()))
	sys.stdout.flush()
#root.walkPrint(root)
print str(time.ctime())
print "exporting to matlab file"
#root.exportMatrix()
root.exportMultiLineMatrix()
root.exportCrawled_sites()
root.exportUnique_sites()
print str(time.ctime())
sys.exit()

#--------------------------------------------

'''
This is a problem I ran into and didnt know where else to document it
Problem: sites containing non ascii chars.
Solution: http://plone.org/products/linguaplone/issues/58

Added byGoffinet FrancoisonFeb 01, 2007 03:03 PM
I know the same problem with french translation. After an update of all concerned products, I created a $PYTHON//site-packages/sitecustomize.py filethat modify the python's default codec in utf8 :

import sys
sys.setdefaultencoding('utf8')

I restarted my instance and I do not have any UnicodeDecodeError.'''
#end
