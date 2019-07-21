from habanero import Crossref
import pandas as pd
import bibtexparser
from bibtexparser.bparser import BibTexParser
import datetime

work = Crossref()
parser = BibTexParser()
parser.ignore_nonstandard_types = False
parser.homogenise_fields = False
parser.common_strings = False

common_words = ['a','the','on','an','for','of','at','with', 'without', 'toward',
                'towards', 'not', 'but', 'in', 'is', 'are', 'that', 'and', 'or',
                'learning','into','to','its','which','do','does','using','via',
                'from']

def doisearcher(origtitle, inauthor, year):
    words = origtitle.split()
    new_words = [i for i in words if i.lower() not in common_words]
    title = ' '.join(new_words)
    print(title)
    print(inauthor)
    w1 = work.works(query_title=title,
                    #query_author=inauthor,
                    select=['title','DOI'],
                    cursor="*", limit=1000,
                    sort='relevance', order = "desc"
                    )
    w2 = []
    for z in w1:
        w2 = w2 + [item for item in z['message']['items']]
    return w2, new_words

bibtext = pd.read_csv('bibtext.csv', encoding='ISO-8859-1')
for k,row in bibtext.iterrows():
    bib = bibtexparser.loads(row[0], parser)


outdf = pd.DataFrame()
#print(bib.entries[0:5])
for bibitem in bib.entries:
    intitle = bibitem['title']
    inauthor = bibitem['author'].split()[0]
    inauthor = inauthor.replace(',','')
    year = bibitem['year']
    w, words = doisearcher(intitle, inauthor, year)
    for item in w:
        titleword = item['title'][0].split()
        titleword = [x.lower() for x in titleword]
        if all(x.lower() in titleword for x in words):
            newrow = pd.Series([bibitem['ID'], intitle,item['title'][0],item['DOI']],
                                index=['ID','orig_title','doi_title','doi'])
            print(newrow)
            outdf = outdf.append(newrow, ignore_index=True)

    outdf.to_csv('DOI.csv')
