Movie-Searcher: Search movies for You
=======================================

when using this library you can get movies download urls easily

Usage
=====

Make a search for movie,for example,which named '功夫',using movie-searcher

.. code-block:: pycon

    >>> from movie_searcher import Searcher
    >>> searcher = Searcher()
    >>> r = searcher.getUrls('功夫')


Installation
============

.. code-block:: shell

    $ pipenv install movie_searcher

Only Python3 is supported