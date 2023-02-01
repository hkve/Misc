# Wikipedia Racer

This is a script to find the shortest path between two Wikipedia pages, based on clickable links in the Wikipedia articles. As an example, consider going from George Washington to Abraham Lincoln. In the George Washington article, there might be a link referring to "list of American presidents". Clicking on that page you will most definitely find Abraham Lincoln. This is a path between George Washington and Abraham Lincoln, however it might not be the shortest, if there is an Abraham Lincoln link present in the George Washington article.

To run the script, you will need the `networkx` package. 

At the very bottom of the script, there are two strings: 
```Python3
start_url = "https://en.wikipedia.org/wiki/Britney_Spears"
end_url = "https://en.wikipedia.org/wiki/Flagellant"
```
Change these to whatever you want, and the script will spit out the *first* shortest path it finds. This is most definitely not unique and the script can easily (be removing some checks) be extended to find every path with the same number of steps