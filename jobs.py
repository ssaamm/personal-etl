from __future__ import print_function

from collections import namedtuple
import itertools as it
import os
import multiprocessing
import logging

import requests
from bs4 import BeautifulSoup

from utils.common import gc
from utils.append_to_spreadsheet import append_to_spreadsheet

hyperlink = '=HYPERLINK("https://indeed.com{url}", "URL")'
key = '1_CsvRPqVPLqwDfMUJjHTQarFwp09IfPX7ON9pyFqxB0'
doc = gc.open_by_key(key)
sheet = doc.get_worksheet(0)
para_sheet = doc.get_worksheet(2)


def str_eq(a, b):
    return a.lower().strip() == b.lower().strip()


class Job(namedtuple('Job', ['title', 'company', 'url'])):
    def __eq__(self, other):
        return other.url == self.url or (str_eq(self.title, other.title) and str_eq(self.company, other.company))


def get_joblink(jobtitle):
    return jobtitle.find('a').get('href')

def get_jobs(url):
    """ url should be an Indeed URL """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    for posting in soup.find_all(attrs={'data-tn-component': 'organicJob'}):
        jobtitle = posting.find(attrs={'class': 'jobtitle'})
        company = posting.find(attrs={'class': 'company'})

        joblink = get_joblink(jobtitle)

        yield Job(title=jobtitle.get_text().strip(), company=company.get_text().strip(), url=joblink)

def existing_jobs():
    rows = sheet.get_all_values()

    for row in it.islice(rows, 1, None):
        if all(not v for v in row):
            raise StopIteration
        yield Job(row[0], row[1], row[2])

def existing_descs():
    descs = para_sheet.col_values(1)
    return descs

def download_job(filepath_job):
    filepath, job = filepath_job
    try:
        r = requests.get('https://www.indeed.com' + job.url)
    except requests.ConnectionError:
        logging.exception('Problem getting %s', job.title)
        return

    with open(filepath, 'wb') as f:
        f.write(r.content)

def download_all_jobs(directory=os.path.expanduser('~/Downloads/job_listings/')):
    all_jobs = list(existing_jobs())
    to_dl = [(os.path.join(directory, '{}.html'.format(ndx)), job)for ndx, job in enumerate(all_jobs)]

    p = multiprocessing.Pool(8)
    p.map(download_job, to_dl)
    p.close()

def push_to_sheets():
    BASE = os.path.expanduser('~/Downloads/job_listings')
    seen_descs = set(existing_descs())

    def get_soup(fpath):
        with open(fpath, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        return soup

    next_row = 4760

    for fn in os.listdir(BASE):
        soup = get_soup(os.path.join(BASE, fn))
        paras = soup.find_all(['p', 'ul', 'ol'])

        for p in paras:
            if p.text in seen_descs:
                logging.info('Skipping "%s"', p.text)
                continue
            next_row = append_to_spreadsheet(None, [p.text], 3, next_row, sheet=para_sheet)
            seen_descs.add(p.text)

TASK = 'push_to_sheets'

if __name__ == '__main__':
    seen_jobs = list(existing_jobs())
    next_row = 1
    new_jobs = 0
    urls = [
        'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=python+kafka+%22data+science%22&as_not=&as_ttl=&as_cmp=&jt=all&st=&salary=&radius=25&l=denver%2C+co&fromage=any&limit=10&sort=date&psf=advsrch',
        'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=python+kafka+%22data+science%22&as_not=&as_ttl=&as_cmp=&jt=all&st=&salary=&radius=25&l=austin%2C+tx&fromage=any&limit=10&sort=date&psf=advsrch',
    ]

    for job in it.chain.from_iterable(get_jobs(u) for u in urls):
        existing_match = next((j for j in seen_jobs if j == job), None)
        if existing_match is not None:
            print('Seen', job)
            continue

        row = (job.title, job.company, hyperlink.format(url=job.url))
        next_row = append_to_spreadsheet(None, job, 0, next_row, sheet=sheet)
        new_jobs += 1

    print('Found', new_jobs, 'new listings')
elif TASK == 'gather':
    download_all_jobs()
elif TASK == 'push_to_sheets':
    push_to_sheets()
