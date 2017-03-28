from __future__ import print_function

from collections import namedtuple
import itertools as it

import requests
from bs4 import BeautifulSoup

from utils.common import gc
from utils.append_to_spreadsheet import append_to_spreadsheet

hyperlink = '=HYPERLINK("https://indeed.com{url}", "URL")'
key = '1_CsvRPqVPLqwDfMUJjHTQarFwp09IfPX7ON9pyFqxB0'
sheet = gc.open_by_key(key).get_worksheet(0)
Job = namedtuple('Job', ['title', 'company', 'url'])


def get_joblink(jobtitle):
    return jobtitle.find('a').get('href')

def get_jobs(term='python'):
    r = requests.get('https://www.indeed.com/jobs?as_and=&as_phr=&as_any={t}&as_not=&as_ttl=&as_cmp=&jt=fulltime&st=&salary=&radius=25&l=austin%2C+tx&fromage=any&limit=50&sort=date&psf=advsrch'.format(t=term))
    soup = BeautifulSoup(r.text, 'html.parser')

    for posting in soup.find_all(attrs={'itemtype': 'http://schema.org/JobPosting'}):
        jobtitle = posting.find(attrs={'class': 'jobtitle'})
        company = posting.find(attrs={'class': 'company'})

        joblink = get_joblink(jobtitle)

        yield Job(title=jobtitle.get_text().strip(), company=company.get_text().strip(), url=joblink)

def existing_jobs():
    all_cols = [sheet.col_values(ndx) for ndx in (1, 2, 3)]

    for row in it.islice(zip(*all_cols), 1, None):
        if all(not v for v in row):
            raise StopIteration
        yield Job(row[0], row[1], row[2])

if __name__ == '__main__':
    seen_urls = {j.url for j in existing_jobs()}
    next_row = 1
    new_jobs = 0

    for job in get_jobs('kafka python'):
        if job.url in seen_urls:
            continue

        row = (job.title, job.company, hyperlink.format(url=job.url))
        next_row = append_to_spreadsheet(None, job, 0, next_row, sheet=sheet)
        new_jobs += 1

    print('Found', new_jobs, 'new listings')
