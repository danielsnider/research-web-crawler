#Web Crawler Fever
A simple breadth first web crawler implemented in python to map web interconnections

##Usage
Linux: `./v2-blog-link-crawler.py`

Optionally a crawl depth argument can be given to limit the number of link traversals to follow with `-d [#]`.

##Description
Starts with an initial website and records what websites are hyperlinked. Those links are traversed and the cycle repeats. Website mappings are stored in a matrix and two other files listed below.

##Output Files
Three files are created. "crawled"  contains the URLs of each site that has been crawled. "unique" contains the URLs of each site found to be unique may or may not be crawled. "matrix" contains an adjacency matrix where each unique site has a row and column. 

##Tips
**How to change the initial node:**
Go to the line of code that says root = Node(".....”) and put a site where the …..s are. The URL must contain blogspot or wordpress in the URL. The default crawl start point is: http://awkwardprops.blogspot.com/

**How to ignore a site or domain so that it not crawled or collected:**
Add a line of code near the other lines like these blacklist.append("http://2chan.us/"). Add another site with the same style.

**How to change how often data is saved:**
Change the global variable “save_data_frequency”. Unit is seconds.

##Thoughts
I found that art blogs and anime blogs expand rapidly, but a real-estate blog and a music blog expanded more slowly.
