# -*- encoding:utf-8 -*-
import requests
import re
import urllib
from multiprocessing.dummy import Pool as ThreadPool


class Searcher:

    __slots__ = ['__pool', '__AllPageDetailsUrlList', '__searchUrl', '__searchDomain', '__downloadDomain', '__params']

    def __init__(self):
        self.__pool = ThreadPool(8)
        self.__AllPageDetailsUrlList = []
        self.__searchUrl = "http://s.ygdy8.com/plus/so.php"
        self.__searchDomain = 'http://s.ygdy8.com'
        self.__downloadDomain = 'http://www.ygdy8.com'
        self.__params = {"kwtype": "0", "searchtype": "title", "keyword": "leetao"}

    def __searchMoviesResults(self, url=None, params=None):
        if url is not None:
            if params is not None:
                params['keyword'] = params['keyword'].encode('gb2312')
                params = urllib.parse.urlencode(params)
                tempResults = requests.get(url, params=params)
            else:
                tempResults = requests.get(url)
        else:
            if params is not None:
                tempResults = requests.get(self.__searchUrl, params=params)
            else:
                tempResults = requests.get(url)
        tempResults.encoding = 'gb2312'
        return tempResults.text

    def __getMoviesDetailPage(self, searchResults):
        """
        get the detailPage's url of movies by using regx
        """
        pattern = re.compile(r"<td\s+width='\d+%'><b><a\s+href='(.*\.html)'\s*>")
        allDetaiPages = pattern.findall(searchResults)
        return allDetaiPages

    def __getPageNumTotal(self, searchResults):
        """
        get the total number of pages
        """
        PageNumTotalPattern = re.compile(r"<td\s+width='30'><a\s+href='.+PageNo=(\d+)'\s*>")
        PageNumTotal = PageNumTotalPattern.findall(searchResults)
        if len(PageNumTotal) == 0:
            return -1
        else:
            return int(PageNumTotal[0])

    def __nextPageDetail(self, searchResults):
        """
        get the next page'url which lacks the pagenumber
        """
        nextPagePattern = re.compile(r"<td\s+width='30'><a href='(.*PageNo=)\d+'>")
        nextPageUrl = nextPagePattern.findall(searchResults)
        return str(nextPageUrl[0])

    def __getSearchContentByUrl(self, nextPageUrl, pagenumtotal):
        """
        get remain pages's url
        """
        for pageno in range(2, pagenumtotal + 1):
            if pageno is not None:
                url = self.__searchDomain + nextPageUrl + str(pageno)
                res = self.__searchMoviesResults(url)
                return self.__getMoviesDetailPage(res)

    def __getMovieContentsUrl(self, url, params=None):
        """
        get the first page of searching results
        and  get the remain pages's results
        """
        firstPageResults = self.__searchMoviesResults(url, params)
        firstPageResultsList = self.__getMoviesDetailPage(firstPageResults)
        # get the remain pages's results
        TotalPageNum = self.__getPageNumTotal(firstPageResults)
        if TotalPageNum > 0:
            nextPageUrl = self.__nextPageDetail(firstPageResults)
            remainPageResultsList = self.__getSearchContentByUrl(nextPageUrl, TotalPageNum)
            self.__AllPageDetailsUrlList.extend(remainPageResultsList)

        self.__AllPageDetailsUrlList.extend(firstPageResultsList)
        return self.__AllPageDetailsUrlList

    def __getMovieDownUrl(self, downPageUrlList):
        """
        for url in downPageUrlList:
             downPageContentUrl = self.__downloadDomain + str(url)
             downPageContent = self.__searchMoviesResults(downPageContentUrl)
             resultsList.append(self.__getDownPageContentUrl(downPageContent))
        """
        resultsList = []
        downPageContentList = []
        downPageContentUrlList = [(self.__downloadDomain + url) for url in downPageUrlList]
        resultsList.append(self.__pool.map(self.__getDownPageContentUrl,
                                           self.__pool.map(self.__searchMoviesResults, downPageContentUrlList)))
        self.__pool.close()
        self.__pool.join()
        return resultsList

    def __getDownPageContentUrl(self, downPageContent):
        downPattern = re.compile(r'<td.+><a\s+href="(.+)"\s*>')
        ftpUrlList = downPattern.findall(downPageContent)
        if len(ftpUrlList) > 0:
            ftpUrl = ftpUrlList[0]
        else:
            ftpUrl = "unknown"
        return ftpUrl

    def getUrls(self, movie_name):
        self.__params['keyword'] = movie_name
        try:
            urlList = self.__getMovieContentsUrl(self.__searchUrl, self.__params)
            if len(urlList) == 0:
                return []
            else:
                allDownLoadUrlList = self.__getMovieDownUrl(urlList)
                movie_url_list = [url for url in allDownLoadUrlList[0] if url[-3:] not in ['zip', 'rar','exe'] and url != 'unknown']
                return movie_url_list
        except Exception as e:
            return [str(e)]
