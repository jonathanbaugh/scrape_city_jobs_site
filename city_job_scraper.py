# -*- coding: utf-8 -*-
"""
Created on Thurs Oct 10 2017
Author: Christopher Dolph
"""

import requests
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd

SEARCH_LINK_SUBSTR = 'https://www.austincityjobs.org'


def get_html(url,verify = True):

    """get_html uses requests to return a raw html string from a url"""

    r = requests.get(url,verify = verify)
    raw_html = r.text

    return raw_html


def get_pages():

    """ get_pages returns a list of urls from the City of Austins job search site
	the length of which is equal to the number of pages containing job postings. This
	number will vary according to the total number of jobs advertised on the site."""

    search_link = 'https://www.austincityjobs.org/postings/search'
    site_html = get_html(search_link, False)
    page_soup = BeautifulSoup(site_html, 'html.parser',parse_only=SoupStrainer('div',{"class":"pagination"}))
    pagination = page_soup.find_all(href =True)
    pages_to_append = list(set([a['href'] for a in pagination]))

    pages = ['https://www.austincityjobs.org/postings/search?page=1']

    for i in pages_to_append:
        pages.append(SEARCH_LINK_SUBSTR + i)

    pages.sort()

    return pages


def get_job_links(some_html):
    """get_job_links works on a single webpage. It returns a list of urls to the current job postings on the City of Austin's website.
    It takes a raw html string as a argument and parses it using BeautifulSoup """
    job_links = []

    links_soup = BeautifulSoup(some_html, 'html.parser',parse_only=SoupStrainer('td',{"class":"job-title"}))

    for link in links_soup.find_all('a'):
        job_links.append(SEARCH_LINK_SUBSTR + link.get('href'))

    return job_links


def compile_links():
    """compile_links consolidates lists of urls generated by get_job_links into one list """

    pages_to_parse = get_pages()
    all_links = []

    for i in pages_to_parse:
        html = get_html(i,False)
        all_links += get_job_links(html)

    return all_links

def get_tables(link):

     """ get tables collects table row data from an html table on a webpage"""

     html = get_html(link,False)
     table_soup = BeautifulSoup(html, 'html.parser')
     table = table_soup.find_all("tr")

     return table

def get_headers(table_rows):

    """get_headers gathers only the th tags from an html table to set the headers for a csv export"""

    headers = [i.find('th').text for i in table_rows]

    return headers


def get_rows(table):

    """get_rows gathers only the td tags from an html table for a csv export"""

    row = [i.find('td').text for i in table]

    return row


def build_dataframe(links):

    """build_dataframe constructs a pandas dataframe one row at a time, where row is the
    html table data from a url."""

    headers = get_headers(get_tables(links[0])) #look at first link only for headers

    df = pd.DataFrame(columns = headers)

    try:
        for i, link in enumerate(links):
            rows = get_rows(get_tables(link))

            # not all tables are of equal length, some are one column shorter

            if len(rows) < 22:
                rows.append('null')

            df.loc[i] = rows

    finally:

        return df

def main():

    the_links = compile_links()
    data_frame = build_dataframe(the_links)
    data_frame.to_csv('jobs.csv')

#call main()
if __name__ == "__main__":
    main()
