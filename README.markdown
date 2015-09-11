INFO
========

Web-version of tabletop game "Smallworld". Protocol description lies [here][ref2]
Group project for "Programming rechnology" university course.  
Authors: Vasilyeva Elena, Podolsky Leonid, Zemlyannikova Natalya.

SYSTEM REQUIREMENTS
========
 
* Python 2.7
* sql-alchemy 0.6.8
* Apache HTTP Server 2.2.17 or higher
* mod_wsgi 3.3 or higher

DEPLOYMENT
=========

Configure apache + mod_wsgi like [here][ref] to run small_worlds.py script. Run `python parseJson.py resetServer` to **reset server**.


[ref]: http://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide
[ref2]: https://github.com/vkevroletin/web-game-doc
