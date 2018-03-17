from movie_searcher import Searcher

def test_getUrls():
    a = Searcher()
    assert isinstance(a.getUrls('功夫'),list) == True
