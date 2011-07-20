Netflexport
===========

Export your Netflix account: ratings, queues, recommendations.  Since Netflix
doesn't have an API for rating export, you'll have to use your browser to
generate a list of rated titles and feed that in.  Take control of your own
data, do whatever you want with it.

This code is likely to decay as I leave the Netflix service behind.  Fork
and improve it as you will.  Note one of the underlying libraries relies on
Netflix API v1.0 while all of the calls in this application are to the API
v2.0.  Forking that and moving it to v2.0 may make for much more interesting
ways to manipulate your data right from Netflix.

Requirements
------------

* Python 2.6 or higher (untested on higher versions)
* virtualenv (optional)
* Web browser with JavaScript console (optional, for acquiring ratings list)

Installation
------------

If you're using virtualenv (you should use virtualenv), create one for this
project.  Then run:

```
% pip install -e git+https://github.com/voccs/netflexport.git
% cd src/netflexport
% pip install -r requirements.txt
```

You could do this in your standard Python installation, too, but that'll
just leave a bunch of cruft sitting around.

Usage
-----

1. Run this snippet of JavaScript in your browser's equivalent of a JavaScript
console on each and every page of your [ratings][1], copying and pasting the
console output to a text file.  The output format, in case you want to use
your own alternative for generating it, is one catalog title identifier number
per line.

```
jQuery('tr.agMovie').each(function(i,el){console.log(jQuery('a.mdpLink', this).attr('id').slice(2,-2))});
```

Save the text file to, say, `ratings.txt`.

2. [Acquire API credentials][2] and put them in settings.cfg.

3. [Generate your own authorization token][3] and put the key, secret,
and user ID in settings.cfg.local, copying the structure over from
settings.cfg.

4. Run it:

```
% python netflexport -c settings.cfg -r ratings.txt > netflix.json
```

It will skip over fetching ratings if no ratings file is provided;
there is a ratings setting in settings.cfg to record the file location.

5. The export is to STDOUT to a concatenation of JSON structures, like:

```
{
    "disc_queue": [
       { "item" : { ... } },
       ...
    ],
    "instant_queue": [
       { "item" : { ... } },
       ...
    ],
    "ratings": [
       { "catalog_title: ... },
       ...
    ],
    "recommendations": [
       { "average_ratings": ... },
       ...
    ]
}
```

[1]: http://movies.netflix.com/MoviesYouveSeen
[2]: http://developer.netflix.com/member/register
[3]: http://developer.netflix.com/walkthrough
