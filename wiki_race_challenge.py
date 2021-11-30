import networkx as nx
import re
import requests as req

def get_html(url, params=None, output=None):
	"""
	Takes an url and returns a string of the html displayed on that page. Optionally
	parameters can be used to request specific information. The html string can also
	be saved to a file.

	Args:
		url (str): The url to request html from
		params (dictionary[str, str], optional): Paramaters to be passed to request. Defualts to None
		output (str): Filename to save the retrieved html. Defaults to None

	Returns:
		html_str (str): A string containing the urls html.   
	"""

	response = req.get(url, params=params)
	html_str = response.text

	if output is not None:
		with open(output, "w+") as file: file.write(html_str)

	return html_str

def reversed_range(urls):
	"""
	Returns an inverse range, used for backwards iteration

	Args:
		urls (list[str]): List to create backwards range

	Returns:
		(range): Range iterating the urls list backwards
	"""
	return range(len(urls)-1, -1, -1)

def check_dupes(urls):
	"""
	Checks for duplicates of url list. 

	Args:
		urls (list[str]): List of urls to check for duplicates

	Returns:
		(boolean): True/False if duplicates are found
	"""
	if len(urls) == len(set(urls)):
		return False
	else:
		return True

def remove_dupes(urls):
	"""
	Removes dupes from url list, since dictionary keys must be unique. 

	Args:
		urls (list[str]): List of urls possibly containing duplicates

	Returns:
		(list[str]): List of unique urls
	"""
	return list(dict.fromkeys(urls))

def find_urls(html_str, base_url=None, output=None):
	"""
	Takes a html string and searches for all urls contained inside anchor tags (<a ... >).
	Fragment identifiers (links that start with #) are ignored. If a base url is given, 
	links with a # inside will be split, where the urls before the # is concatenated 
	with the base url. Can also write the results to a file. 

	Args:
		html_str (str): The string of html to parse
		base_url (str, optional): Base url to add to the link after the fragment identifier has been removed
		output (str, optional): Filename to write the links found
	
	Returns:
		urls (list[str]): The urls found inside the html string.
	"""


	# Get everything inbetween '<a' and first '>'
	anchors = re.findall("(?<=<a)(.*?)(?=>)", html_str)
	
	# List to store only anchors that contain a href paramter. 
	raw_url = []

	# Iterate over all anchor tags
	for i in range(len(anchors)):
		# Get everything inbetween 'href="' and first '"'
		possible_url = re.findall("(?<=href=[\"|\'])(.*?)(?=[\"|\'])", anchors[i])
		
		# Only add to raw_url if there is a href present inside the anchor tag
		if not possible_url == []: raw_url.append(*possible_url)

	# List to store formatted urls
	urls = []

	# Loop over every recognized url
	for url in raw_url:

		# If url on contain a fragment, ignore it 
		if url.startswith("#"):
			continue

		# If the url contains a fragment and a base_url is given, concatenate non-fragment part with base_url
		elif "#" in url and base_url is not None:
			relative_path = url.split("#")[0]
			urls.append(base_url+relative_path)
		
		# If not, we assume the url is good
		else:
			urls.append(url)

	# Iterate over all urls and add correct protocol
	for i in range(len(urls)):

		# If link does not start with https, add it
		if urls[i].startswith("//"):
			urls[i] = "https:" + urls[i]

		# If url is a relative link, add the base url
		elif not urls[i].startswith("https://") and base_url is not None:
			urls[i] = base_url + urls[i]
	
	# Remove duplicate links
	if check_dupes(urls): urls = remove_dupes(urls)
	
	# Optional write to file
	if not output is None: write_urls(urls, output)

	return urls

def find_articles(html_str, output=None):
	"""
	Takes a html_str belonging to a wikipedia article and returns all article urls presenent on that page.
	Returns urls in any language. Optionally write the results to a file.

	Args:
		html_str (str): Html string of the wikipedia article to parse
		output (str, optinal): Filename to write the article urls found

	Returns:
		urls (list[str]): Contains all the article urls found
	"""

	# Get all urls, with fragments concatenate with the english wikipedia. 
	urls = find_urls(html_str, base_url="https://en.wikipedia.org")

	# Remove urls with a ":" present, except if it is followed by an underscore. 
	# This should exclude namespaces, but include article on the form "Title: subtitle"
	namespace_src = re.compile(":[^_]")

	# Only include articles. Note that this will include other languages.
	article_src = re.compile(r"wikipedia.org/wiki/")


	# Iterate backwards since we will delete urls not fitting our patters. 
	for i in reversed_range(urls):
		# Delete if url contains namespace
		if not re.search(namespace_src, urls[i][6:]) is None:
			del urls[i]
		
		# Delete if url does not fit article url structure
		elif re.search(article_src, urls[i]) is None:
			del urls[i]

	for i in reversed_range(urls):
		if "Main_Page" in urls[i]:
			del urls[i]

	# Optional write to file
	if not output is None: write_urls(urls, output)

	return urls

def keep_english(articles):
	"""
	Function to only keep english articles from a list of articles. Checks if the article url 
	starts with "en."

	Args:
		articles (list[str]): List of strings containing article urls
	Returns:
		articles (list[str]): List of strings containing only english article urls
	"""
	for i in reversed_range(articles):
		if not "https://en." in articles[i]:
			del articles[i]
	return articles

def find_english_articles(article):
	"""
	Helper function to simply pass in an article url and get the linked english articles

	Args:
		article (str): Url to article where one should find the articles

	Returns:
		list[str]: List containing the english wikipedia articles present on "article" wikipedia page
	"""
	return keep_english(find_articles(get_html(article)))

def find_english_articles_reversed(article):
	"""
	Function to look for urls that link to a specific article. Every wikipedia page has a special page
	..."/Special:WhatLinksHere/Article_Name" that lists all urls leading to that page.

	Args:
		article (str): Url to wiki article where one wants to find the wiki article urls that point to this page

	Returns:
		articles (list[str]): List off all wiki urls that lead to article
	"""
	reverse_link_standard_url = "https://en.wikipedia.org/wiki/Special:WhatLinksHere/"
	article_end = article.split("wiki/")[-1]	

	reverse_url = reverse_link_standard_url + article_end

	articles = find_english_articles(reverse_url)

	return articles


def find_end_nodes_forward(G):
	"""
	Finds all nodes in a graph G that has out degree 0. This means all nodes in the graph that currently 
	points to no other article. 

	Args:
		G (nx.DiGraph): Graph containg the nodes on wishes to find.

	Returns:
		nodes (list[nx.node]): All nodes with out degree 0. 
	"""
	nodes = []
	for node, deg in G.out_degree(G.nodes()):
		if deg == 0: nodes.append(node)

	return nodes

def find_end_nodes_backward(G):
	"""
	Finds all nodes in a graph G that has in degree 0. This means all nodes in the graph that currently 
	has no article poitning to it. This is required for the H graph shortest_path since it searces
	from the end_url.  

	Args:
		G (nx.DiGraph): Graph containg the nodes on wishes to find.

	Returns:
		nodes (list[nx.node]): All nodes with in degree 0. 
	"""
	nodes = []
	for node, deg in G.in_degree(G.nodes()):
		if deg == 0: nodes.append(node)

	return nodes	

def add_layer_forward(G, prev_article, articles):
	"""
	Adds a new layer to a graph, pointing forward. If one starts at start_url, this function adds all 
	"articles" to the graph that start_url referes to. 

	Args:
		G (nx.DiGraph): Graph to add new nodes to
		prev_article (str): Url to article leading to articles
		articles (list[str]): List of urls that can be reached from prev_article
	"""
	for article in articles:
		G.add_node(article)
		G.add_edge(prev_article, article)

def add_layer_backward(G, prev_article, articles):
	"""
	Adds a new layer to a graph, pointing backward. If one starts at end_url, this function adds all 
	"articles" as nodes that leads to start_url. Note that the argument of G.add_edge is swapped
	compeared to add_layer_forward. This is because the article leads to prev_article (since we are searching backwards).

	Args:
		G (nx.DiGraph): Graph to add new nodes to
		prev_article (str): Url to article leading to articles
		articles (list[str]): List of urls that can be reached from prev_article
	"""
	for article in articles:
		G.add_node(article)
		G.add_edge(article, prev_article)

def write_to_file(filename, path):
	"""
	Write paths to a file "filename". The points in the path are separated by newlines.
	"""
	try:
		with open(filename, "w+") as file:
			for article in path:
				file.write(article + "\n")
	except FileNotFoundError:
		print(f"Chould not write {filename}")
def found_path(G, H):
	F = nx.compose(G,H)	
	if nx.has_path(F, source=start_url, target=end_url):
		return True
	else:
		return False	

def shortest_path(start_url, end_url, filename=None, silent=False, max_depth=7):
	"""
	Main function, and the implementation of the double-ended directional graph. The graph G contains the
	forward search, while H contains the backward search. At each "depth", the algorithm looks for all
	articles adds a new layer of articles leading from (forward) or leading to (backward) the last
	layer of the two graphs. After an article is added, a new graph F is constructed, composed of G and H.
	It checks if there is a path from start_url to end_url in F. If so, the paths has been found.

	Args:
		start_url (str): The url where the path should start
		end_url (str): The url where the path should end
		filename (str): Name of the file where the path(s) should be saved. Defaults to None
		silent (bool): If nothing should be printed to the terminal. Defaults to False
		max_depth (int): How many layers to consider from each side. Defaults to 7 
	"""

	# Start info
	if not silent:
		print("I will find the shortest path from:")
		print(start_url)
		print("To:")
		print(end_url)
		print("I might take a while, but do not bother me!")
		print("\n")

	# Graph for FORWARD search
	G = nx.DiGraph()

	# Graph for BACKWARD search
	H = nx.DiGraph()

	# Firist node of FORWARD/BACKWARD
	G.add_node(start_url)
	H.add_node(end_url)

	# Count how many layers has been added, and store if a path has been found
	depth = 0
	found = False

	# Main loop
	while not found and depth < max_depth:
		
		# Find all in-degree/out-degree = 0 nodes  
		G_end_nodes = find_end_nodes_forward(G)
		H_end_nodes = find_end_nodes_backward(H)

		# Add to the forward layer
		for g in G_end_nodes:

			# New articles leading forward
			new_nodes_forward = find_english_articles(g)

			# Add the new articles to G
			add_layer_forward(G, g, new_nodes_forward)
			
			# Check if a path has been found
			found = found_path(G, H)
			if found: break

		# If the path was found by adding forward layer, break the search loop
		if found: break

		# Add to the backward layer
		for h in H_end_nodes:

			# New articles leading backward
			new_nodes_backward = find_english_articles_reversed(h)
			
			# Add the new articles to H
			add_layer_backward(H, h, new_nodes_backward)
			
			# Check if a path has been found
			found = found_path(G, H)
			if found: break

	# Now that the search is done, find the path and do optional printing/write to file
	if found:
		F = nx.compose(G,H)
		path = nx.shortest_path(F, source=start_url, target=end_url)
			
		if not silent:
			print("I found the path:")
			for url in path: print(url)

	# If not found after reaching max_depth, be sad
	else:
		print("I did not find any path :( Im sorry")
		if max_depth == depth: 
			print("I reached max depth of {max_depth} while searching.")
			print("If you want a deeper search, increase max_depth")

	# Optional write to file.
	if filename is not None and found: write_to_file(filename, path)

if __name__ == "__main__":
	# The example from the assignment
	start_url = "https://en.wikipedia.org/wiki/Britney_Spears"
	end_url = "https://en.wikipedia.org/wiki/Flagellant"
	shortest_path(start_url, end_url)