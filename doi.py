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

# This list contains words that are not decisive to identify the publications,
# such as articles and adverbs. They must be removed because the Crossref
# API retrieves all the publications whose titles that have at least a word 
# in common with the publication under analysis
common_words = ['a','the','on','an','for','of','at','with', 'without', 'toward',
                'towards', 'not', 'but', 'in', 'is', 'are', 'that', 'and', 'or',
                'learning','into','to','its','which','do','does','using','via',
                'from']

def doisearcher(origtitle, inauthor):
    """
    This function calls the Crossref API and returns the most relevant publications
    whose title has at least one word in common with the input title (origtitle).
    This list is limited to the first 1000 entries.
    It is possible to run the search on the list of authors. In this version, this
    option is commented out.
    :param origtitle: title of the input publication 
    :param inauthor: list of authors of the input publication
    :return: the list of the matched publications (w2) and the title of the 
    publication under analysis without the common words (transformed into a 
    list of words).
    """
    words = origtitle.split()
    new_words = [i for i in words if i.lower() not in common_words]
    title = ' '.join(new_words)
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

# Retrieving the list of BibTex-formatted publications 
bibtext = pd.read_csv('bibtext.csv', encoding='ISO-8859-1')
for k,row in bibtext.iterrows():
    bib = bibtexparser.loads(row[0], parser)

outdf = pd.DataFrame()
# Searching the DOIs of each publication in the input bibtext file and returning
# them as a CSV file
for bibitem in bib.entries:
    intitle = bibitem['title']
    inauthor = bibitem['author'].split()[0]
    inauthor = inauthor.replace(',','')
    w, words = doisearcher(intitle, inauthor)
    for item in w:
        titleword = item['title'][0].split()
        titleword = [x.lower() for x in titleword]
        if all(x.lower() in titleword for x in words):
            newrow = pd.Series([bibitem['ID'], intitle,item['title'][0],item['DOI']],
                                index=['ID','orig_title','doi_title','doi'])
            print(newrow)
            outdf = outdf.append(newrow, ignore_index=True)

    outdf.to_csv('DOI.csv')
