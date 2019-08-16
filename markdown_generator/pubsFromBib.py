#!/usr/bin/env python
# coding: utf-8

# # Publications markdown generator for academicpages
# 
# Takes a set of bibtex of publications and converts them for use with [academicpages.github.io](academicpages.github.io). Use bibtextparser instead 
# 


import bibtexparser as btp
from time import strptime
import string
import html
import os
import re
import sys

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
# TODO: use a command line argument
try:
    with open('bibtex.bib') as bibFile:
        bibData = btp.load(bibFile)
except IOError:
    print("Could not find bibtex.bib")
    sys.exit(1)


# GOOGLE SCHOLAR EXAMPLE OUTPUT
# {u'title': u'Step-level person localization through sparse sensing of structural vibration', u'booktitle': u'proceedings of the 14th international conference on information processing in sensor networks', u'author': u'Mirshekari, Mostafa and Pan, Shijia and Bannis, Adeola and Lam, Yan Pui Mike and Zhang, Pei and Noh, Hae Young', 'ENTRYTYPE': u'inproceedings', u'year': u'2015', u'organization': u'ACM', 'ID': u'mirshekari2015step', u'pages': u'376--377'}

MAX_SLUG_LEN = 25
SITE_NAME = "https://thecodemaiden.com/"
for pubData in bibData.entries:

    #reset default date
    pub_year = "1900"
    #pub_month = "01"
    #pub_day = "01"
    pubID = pubData[u'ID']
    rawTitle = pubData[u'title']
    

    try:
        pub_year = pubData[u'year']
        m = pubData.get(u'month')
        if m is not None:
            pub_month = m
        d = pubData.get(u'day')
        if d is not None:
            pub_day = d

        pub_date = pub_year+"-"+pub_month+"-"+pub_day
       # TODO: just use the 'ID' field as the slug? 
        #strip out {} as needed (some bibtex entries that maintain formatting)
        clean_title = rawTitle.replace("{", "").replace("}","").replace("\\","")
        slug_title = clean_title.replace(" ","-")
        if len(slug_title) > MAX_SLUG_LEN:
            slug_title = slug_title[0:MAX_SLUG_LEN+1]

        url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", slug_title)
        url_slug = url_slug.replace("--","-")

        md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--","-").lower()
        html_filename = (str(pub_date) + "-" + url_slug).replace("--","-").lower()

        #Build Citation from text
        citation = pubData[u'author'] + ". "


        #citation title
        citation = citation + "\"" + html_escape(clean_title) + ".\""

        venue = pubData.get(u'booktitle')
        if venue is None:
            venue = pubData.get(u'journal')
        if venue is None:
            venue = pubData.get(u'ENTRYTYPE')
        #add venue logic depending on citation type

        citation = citation + " " + html_escape(venue)
        citation = citation + ", " + pub_year + "."

        orgname = pubData.get(u'organization')
        if orgname is None:
            orgname = pubData.get(u'publisher')
        if orgname is not None:
            citation = citation + " " + orgname + "."

        
        ## YAML variables
        md = "---\ntitle: \""   + clean_title + '"\n'
        
        md += """collection: publications \n"""

        md += """permalink: """ + html_filename
        
        noteData = pubData.get(u'note')
        if noteData is not None:
            if len(noteData) > 5:
                md += "\nsynopsis: '" + html_escape(noteData) + "'"

        md += "\ndate: " + str(pub_date) 

        md += "\nvenue: '" + html_escape(venue) + "'"
        
        md += "\ncitation: '" + html_escape(citation) + "'"

        md += "\n---"

        
        ## Markdown description for individual page
        if noteData is not None:
            md += "\n" + html_escape(noteData) + "\n"

        urlVal = pubData.get(u'url')
        if urlVal is not None:
            md += "\n[Access paper here](" + urlVal + "){:target=\"_blank\"}\n" 
        else:
            md += "\nUse [Google Scholar](https://scholar.google.com/scholar?q="+html.escape(slug_title.replace("-","+"))+"){:target=\"_blank\"} for full citation"

        md_filename = os.path.basename(md_filename)

        with open("../_publications/" + md_filename, 'w') as f:
            f.write(md)
        print('SUCESSFULLY PARSED {} "{}"'.format(pubID, rawTitle[:60],"..."*(len(rawTitle)>60)))
    # field may not exist for a reference
    except KeyError as e:
        print('WARNING Missing Expected Field {} from entry {}: "{}"'.format(e, pubID, rawTitle[:30],"..."*len(rawTitle)>30))
        continue
