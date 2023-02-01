# Wikipedia Racer

This is a script to find the shortest path between two Wikipedia pages, based on clickable links in the Wikipedia articles. As an example, consider going from George Washington to Abraham Lincoln. In the George Washington article, there might be a link referring to "list of American presidents". Clicking on that page you will most definitely find Abraham Lincoln. This is a path between George Washington and Abraham Lincoln, however it might not be the shortest, if there is an Abraham Lincoln link present in the George Washington article.

To run the script, you will need the `networkx` package. 

At the very bottom of the script, there are two strings: 
```Python3
start_url = "https://en.wikipedia.org/wiki/Britney_Spears"
end_url = "https://en.wikipedia.org/wiki/Flagellant"
```
Change these to whatever you want, and the script will spit out the *first* shortest path it finds. This is most definitely not unique and the script can easily (be removing some checks) be extended to find every path with the same number of steps

The approache of the path finding algorithm is to use two graphs, **G** and **H**. Initially **G** has one node, the **start_url** and **H** has one node, the **end_url**. The algorithm searches in "layers", where one layer refers to an article referring to other articles. The **G** graph searches forward, finding all articles that **start_url** leads to, then find all articles that those articles leads to and so on. The **H** graph searches backwards. Starting at **end_url**, it finds all articles that leads to the article **end_url**, then all articles that leads to these articles and so on. This is done by looking at the special pages, i.e.: https://en.wikipedia.org/wiki/Special:WhatLinksHere/Freeman_Dyson. At each added article, a new graph **F** is constructed from **G** and **H**. It finds if a path can be created from **start_url** to **end_url**. If not, it continues searching. 