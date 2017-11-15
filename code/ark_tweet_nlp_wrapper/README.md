ark-tweet-nlp-python
====================

Simple Python wrapper around runTagger.sh of ark-tweet-nlp. It passes a list of tweets to runTagger.sh and parses the result into a list of lists of tuples, each tuple represents the (token, type, confidence). 

Wraps up:

  * https://github.com/brendano/ark-tweet-nlp
  * http://www.ark.cs.cmu.edu/TweetNLP/

Lives here:

  * https://github.com/ianozsvald/ark-tweet-nlp-python

Usage:
-----
   
    >>> import CMUTweetTagger
    >>> print CMUTweetTagger.runtagger_parse(['example tweet 1', 'example tweet 2'])
    >>> [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)], [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]

Note, if you receive:

    >>> Error: Unable to access jarfile ark-tweet-nlp-0.3.2.jar

Make sure you pass in the correct path to the jar file, e.g. if this script is cloned into a subdirectory of ark-tweet-nlp then you may need to use:

    >>> print CMUTweetTagger.runtagger_parse(['example tweet 1', 'example tweet 2'], run_tagger_cmd="java -XX:ParallelGCThreads=2 -Xmx500m -jar ../ark-tweet-nlp-0.3.2.jar")

Notes and possible improvements:
-------------------------------

  * This wrapper calls runTagger.sh's contents via command line, Java takes a few seconds to start - you should send in a list of tweets rather than doing them one at a time
  * Communicating once the shell process is opened rather than closing comms would be more sensible
  * _call_runtagger replaces new-lines in the tweet with a space (as new-lines signify tweet separators in runTagger.sh), this might not be appropriate if you need to maintain new-lines
  * It would probably be awfully nicer if somebody wrapped up a py4J interface so we didn't have to start java at the command line each time (or maybe I shouldn't use .communicate which closes the process and instead keep the process open?)
  * _split_results could do with a unittest, probably the module should turn into a class so you only have to set runTagger.sh's path location once (and it should assert if it can't find the script on initialisation)
  * Really the script should be in a class so it can be initialised with runTagger.sh

License:
-------

*MIT*

Copyright (c) 2013 Ian Ozsvald.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Copyright (c) 2013 Ian Ozsvald

