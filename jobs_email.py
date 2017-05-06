from __future__ import print_function

import datetime as dt
import itertools as it
import smtplib
from email.mime.text import MIMEText

import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

from utils.common import gc
from utils.secrets import GMAIL_USER, GMAIL_PASS, JOBS_RECIPIENT


key = '1_CsvRPqVPLqwDfMUJjHTQarFwp09IfPX7ON9pyFqxB0'
workbook = gc.open_by_key(key)
jobs_sheet = workbook.get_worksheet(0)
meta_sheet = workbook.get_worksheet(1)

DF_SHEETS_OFFSET = 2


def get_rows():
    all_cols = [jobs_sheet.col_values(ndx) for ndx in (1, 2, 5, 3)]

    for row in it.islice(zip(*all_cols), 1, None):
        if all(not i for i in row):
            raise StopIteration()
        yield row


def train_model(all_jobs):
    rated_jobs = all_jobs.dropna()

    pos_examples = rated_jobs[rated_jobs.sounds_cool == 1]
    neg_examples = rated_jobs[rated_jobs.sounds_cool == 0].sample(pos_examples.shape[0])
    undersampled = pd.concat([pos_examples, neg_examples])

    X = undersampled['title'].as_matrix()
    y = undersampled['sounds_cool'].as_matrix()

    vect = CountVectorizer()
    Xp = vect.fit_transform(X).toarray()
    clf = LogisticRegression().fit(Xp, y)

    return clf, vect


def fetch_latest_seen_row():
    return int(meta_sheet.acell('B1').value)


def record_latest_seen_row(rownum):
    meta_sheet.update_acell('B1', rownum)


def format_email(jobs):
    email = []
    job_template = u'{} @ {} - {}'

    for _, row in jobs.iterrows():
        r = requests.get('https://indeed.com' + row['url'])
        email.append(job_template.format(row['title'], row['company'], r.url))

    return '\n\n'.join(email)


def send_email(content):
    msg = MIMEText(content, 'plain', 'utf-8')

    msg['Subject'] = 'Job recommendations for {}'.format(dt.date.today())
    msg['From'] = GMAIL_USER
    msg['To'] = JOBS_RECIPIENT

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(GMAIL_USER, GMAIL_PASS)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

if __name__ == '__main__':
    all_jobs = pd.DataFrame(data=list(get_rows()), columns=['title', 'company', 'sounds_cool', 'url'])
    all_jobs['sounds_cool'] = pd.to_numeric(all_jobs['sounds_cool'])

    clf, vect = train_model(all_jobs)

    latest_seen_row = fetch_latest_seen_row()
    unrated_jobs = all_jobs[all_jobs['sounds_cool'].isnull()]
    unrated_jobs = unrated_jobs.iloc[latest_seen_row - DF_SHEETS_OFFSET:]

    if unrated_jobs.shape[0] == 0:
        print('No new jobs to rate')
        exit(0)

    X = unrated_jobs['title'].as_matrix()
    Xp = vect.transform(X).toarray()

    y_pred = clf.predict(Xp)
    recommended_jobs = unrated_jobs[y_pred > 0.5]  # assume labels are 1 and 0
    content = format_email(recommended_jobs)
    send_email(content)

    record_latest_seen_row(unrated_jobs.index[-1] + DF_SHEETS_OFFSET)
