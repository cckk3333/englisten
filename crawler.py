import argparse
import requests
import urllib.request
import os

from bs4 import BeautifulSoup
from selenium import webdriver

parser = argparse.ArgumentParser()
parser.add_argument("-f", help='file that contains words you want to download', required=True)
parser.add_argument("-d", help='directory to put sound files in', required=True)
parser.add_argument("--dictionary", help='directory to put sound files in', default='cambridge')

args = parser.parse_args()

driver = webdriver.Chrome('/home/mhyang/Desktop/chromedriver')

def download_cambridge(word):
    try:
        driver.get("https://dictionary.cambridge.org/dictionary/english/%s" % word)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        files = []
        for _ in soup.find_all("span"):
            try:
                mp3_file = _["data-src-mp3"]
                if 'us_pron' in mp3_file:
                    files.append(mp3_file)
            except:
                pass
        if not files:
            print('no audio file related to %s' % word)
            return None
        else:
            real_url = 'https://dictionary.cambridge.org' + files[0]
            print(real_url)

        r = urllib.request.urlopen(real_url)
        tmp_fpath = '%s.%s' % (word, real_url.split('.')[-1])
        with open(tmp_fpath, 'wb') as g:
            g.write(r.read())

        return tmp_fpath

    except Exception as e:
        return None

def download(word, directory, dictionary):
    if dictionary == 'cambridge':
        fpath = download_cambridge(word)
    else:
        raise NotImplementedError

    os.rename(fpath, os.path.join(directory, fpath))


def main():
    os.makedirs(args.d, exist_ok=True)
    words = open(args.f).read().split()
    print('words', words)
    for word in words:
        print(word)
        download(word, args.d, args.dictionary)


if __name__ == '__main__':
    main()