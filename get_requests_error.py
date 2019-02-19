#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

def get(url):
    try:
        req = requests.get(url, timeout=10)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        return req.text
    except requests.exceptions.HTTPError as e:
        print(e)


if __name__ == '__main__':
    url = 'www.451sdasfafa.com'
    print(get(url))
