import urllib.request
import gzip
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import psycopg2
import sys
import gc
import time

def create_table(filename: str, cur):
    check_file = Path(f"/var/lib/pubmed/{filename}.xml")
    if not check_file.is_file():
        urllib.request.urlretrieve(f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/{filename}.xml.gz", f"/var/lib/pubmed/{filename}.xml.gz")
        with gzip.open(f"/var/lib/pubmed/{filename}.xml.gz", 'rb') as f_in:
            with open(f"/var/lib/pubmed/{filename}.xml", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        Path(f"/var/lib/pubmed/{filename}.xml.gz").unlink()

    tree = ET.parse(f'/var/lib/pubmed/{filename}.xml')
    root = tree.getroot()

    print("root OK")

    all_registered = root.findall("./PubmedArticle/MedlineCitation/Article/Abstract/AbstractText[@Label='TRIAL REGISTRATION']/../../../..")
    all_registered.extend(root.findall("./PubmedArticle/MedlineCitation/Article/Abstract/AbstractText[@Label='TRIAL REGISTRATION NUMBER']/../../../.."))
    del root
    gc.collect()
    if len(all_registered)==0:
        return(None)

    pmid_list = [x.find("./MedlineCitation/PMID").text for x in all_registered]
    pmid_v_list = [x.find("./MedlineCitation/PMID").attrib.get("Version") for x in all_registered]

    good_indices = list()
    for idx, pmid in enumerate(pmid_list):
        v = pmid_v_list[idx]
        if all([x <= v or pmid != y for x, y in zip(pmid_v_list, pmid_list)]):
            good_indices.append(idx)
    registered = [all_registered[i] for i in good_indices]

    print("registered OK")

    def strOrNone(str):
        if str is None:
            return("")
        else:
            return(str)

    def textOrNone(element):
        if element is None:
            return("")
        else:
            return(element.text)

    names = list()
    pmids = list()
    dois = list()
    article_titles = list()
    journal_titles = list()
    journal_volumes = list()
    journal_issues = list()
    pubyears = list()
    abstracts = [list(), list(), list()]
    for trial in registered:
        namelist = list()
        for author in trial.findall("./MedlineCitation/Article/AuthorList/Author"):
            if (not (author.find("ForeName") is None) and not (author.find("LastName") is None)):
                namelist.append(author.find("ForeName").text + " " + author.find("LastName").text)
            else:
                namelist.append(author[0].text)
        names.append(", ".join(namelist))
        pmids.append(int(trial.find("./MedlineCitation/PMID").text))
        dois.append(textOrNone(trial.find('./PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')))
        article_titles.append(textOrNone(trial.find('./MedlineCitation/Article/ArticleTitle')))
        journal_titles.append(textOrNone(trial.find('./MedlineCitation/Article/Journal/Title')))
        journal_volumes.append(textOrNone(trial.find('./MedlineCitation/Article/Journal/JournalIssue/Volume')))
        journal_issues.append(textOrNone(trial.find('./MedlineCitation/Article/Journal/JournalIssue/Issue')))
        pubyears.append(textOrNone(trial.find('./MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')))
        for abstract_block in trial.findall("./MedlineCitation/Article/Abstract/AbstractText"):
            abstracts[0].append(int(trial.find("./MedlineCitation/PMID").text))
            abstracts[1].append(strOrNone(abstract_block.get("Label")))
            abstracts[2].append(strOrNone(abstract_block.text))


    try:
        cur.execute(f"DROP TABLE IF EXISTS {filename};")
        cur.execute(f"CREATE TABLE {filename} (\
        PMID INT PRIMARY KEY,\
        Names TEXT,\
        DOI VARCHAR(200),\
        ArticleTitle VARCHAR(1152),\
        Journal_Title VARCHAR(717),\
        JournalIssue_Volume VARCHAR(36),\
        JournalIssue_Issue VARCHAR(42),\
        JournalIssue_PubDate_Year VARCHAR(12)\
        );")
    except psycopg2.Error as e: 
        print(f"Error: {e}")

    for idx in range(len(pmids)):
        try:
            cur.execute(f"INSERT INTO {filename} \
                        (PMID,Names,DOI,ArticleTitle,Journal_Title,JournalIssue_Volume,JournalIssue_Issue,\
                        JournalIssue_PubDate_Year) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                        (pmids[idx],
                        names[idx],
                        dois[idx],
                        article_titles[idx],
                        journal_titles[idx],
                        journal_volumes[idx],
                        journal_issues[idx],
                        pubyears[idx]))
        except psycopg2.Error as e: 
            print(f"Error: {e}")

    print("first table OK")
    

    try:
        cur.execute(f"DROP TABLE IF EXISTS {filename}_abstract;")
        cur.execute(f"CREATE TABLE {filename}_abstract (\
        PMID INT NOT NULL,\
        Label TEXT,\
        Text TEXT,\
        index (PMID)\
        );")
    except psycopg2.Error as e: 
        print(f"Error: {e}")
    
    print("before second table")

    for idx in range(len(abstracts[0])):
        try:
            cur.execute(f"INSERT INTO {filename}_abstract\
                        (PMID,Label,Text) VALUES (?, ?, ?);",
                        (abstracts[0][idx],
                        abstracts[1][idx],
                        abstracts[2][idx]))
        except psycopg2.Error as e: 
            print(f"Error: {e}")
    
    print("second table OK")
    Path(f"/var/lib/pubmed/{filename}.xml").unlink()
