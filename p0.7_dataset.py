# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 11:18:31 2023

@author: 12605
"""

import csv
import json
import datetime
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))

def remove_stop_count(s):
    lst = word_tokenize(s)
    f = []
    for w in lst:
        w = w.lower()
        if w not in stop_words:
            f.append(w)
    return len(f)


def author_check(name,li):
    c = 0
    nm = name.split(" ")
    for n in nm:
        if n in li:
            c += 1
    if c == len(nm) or c >= 2:
        return True
    return False

if __name__ == "__main__":
    dic = {}
    total = 0
    reviews =  json.load(open('./p0.3_rxiv_comments/bio_all_preprint_comments.json','r'))
    preprints = json.load(open('./p0_new/total_biorxiv_new.json','r'))
    mult = json.load(open('./p0.2_multiversion/total_biorxiv_multiversion.json','r'))
    trips = json.load(open('./p0.4_trip/bio_all_preprint_trip.json','r'))
    community = json.load(open('./p0.5_community/bio_all_preprint_community.json','r'))
    published = json.load(open('./p0.6_published/p0.6_total_published_boirxiv.json','r'))
    trip_text = ["Peerage of Science","eLife","PeerRef BioMed","RC","GigaByte","ASAPbio crowd review","Biophysics Colab"]
    IF = pd.read_excel('2019-2023JCRImpactFactor.xlsx')
    ifd = {}
    ifd2 = {"Proceedings of the Royal Society B: Biological Sciences":4.637,
            "The American Journal of Human Genetics":10.502,
            "The Journal of Neuroscience":5.673,
            "Genes &amp; Development":9.527,
            "Philosophical Transactions of the Royal Society B: Biological Sciences":5.680,
            "Proceedings of the National Academy of Sciences":9.412,
            "NeuroImage: Clinical":4.350,
            "The American Naturalist":3.744,
            "G3 Genes|Genomes|Genetics":2.781,
            "Cell Host &amp; Microbe":15.923,
            "The ISME Journal":9.180,
            "Genomics, Proteomics &amp; Bioinformatics":7.051,
            "Viruses":3.816,
            "Nature Ecology &amp; Evolution":12.541,
            "The EMBO Journal":9.889,
            "The Plant Cell":9.618,
            "Brain Structure and Function":3.298,
            "The Journal of Physical Chemistry B":2.857,
            "The Plant Journal":6.141,
            "Molecular &amp; Cellular Proteomics":4.870,
            "Nature Structural &amp; Molecular Biology":11.980,
            "The FASEB Journal":4.966,
            "The Journal of Physiology":4.547,
            "The Journal of Immunology":4.886,
            "Cell Death &amp; Disease":6.304,
            "Disease Models &amp; Mechanisms":4.651}
    makeupdic = json.load(open('./check_unpublished/makeup.json','r'))
    
    for i,r in IF.iterrows():
        if not pd.isna(r["journal_name"]) and not pd.isna(r["2020_JCR"]):
            ifd[r["journal_name"].lower()] = r["2020_JCR"]
    # c2 = []
    # cc = 0
            
    
    for doi in preprints:
        try:    
            datev1 = preprints[doi]["1"]["date"]
        except:
            datev1 = 0
        for v in preprints[doi]:
            if doi in dic:
#preprint
                dic[doi]["revisions"] = v
                dic[doi]["last version date"] = preprints[doi][v]["date"]
                if datev1:
                    timegap = (datetime.datetime.strptime(preprints[doi][v]["date"], '%Y-%m-%d') - datetime.datetime.strptime(datev1 , '%Y-%m-%d')).days
                    dic[doi]["revision days since version 1"] += str(timegap) + ";"
            else:
                dic[doi] = {"doi":doi,
                        "first version year": preprints[doi][v]["date"].split("-")[0],
                        "first version date": preprints[doi][v]["date"],
                        "revisions":v,
                        "last version date": preprints[doi][v]["date"],
                        "revision days since version 1":"",
                        "author count": len(preprints[doi][v]["authors"].split(";")),
                        "category": preprints[doi][v]["category"],
                        "reference count":preprints[doi][v]["reference-count"], 
                        "referenced count":preprints[doi][v]["is-referenced-by-count"]}
#comment
                
                dic[doi]["Comment number"] = 0
                dic[doi]["all comment word count"] = 0
                dic[doi]["separated comment word count"] = ""
                dic[doi]["average comment day"] = 0
                dic[doi]["comment days since version 1"] = ""
                counter = 0
                cmt_len = 0
                total_time = 0
                author_cmt = 0
                if doi in reviews:
                    for v2 in reviews[doi]:
                        review_gap_lst = []
                        if reviews[doi][v2] != {}:
                            authors = re.split("; | ",preprints[doi][v]["authors"])
                            try:
                                v_date = preprints[doi][v2[1:]]["date"]
                            except:
                                if doi in mult:
                                    if v2[1:] == mult[doi]["version"]:
                                        v_date = mult[doi]["date"]
                                    elif v2[1:] in mult[doi]["version_history"]:
                                        v_date = mult[doi]["version_history"][v2[1:]]["date"]
                                    
                            for r in reviews[doi][v2]:
                                cmtlen = remove_stop_count(reviews[doi][v2][r]["content"])
                                dic[doi]["separated comment word count"] += str(cmtlen) + ";"
                                cmt_len += cmtlen
                                rvdate = reviews[doi][v2][r]["date"].split(" ")[1:4]
                                rvd = rvdate[0] + "," + rvdate[1] +rvdate[2]
                                if datev1:
                                    reviewgap = (datetime.datetime.strptime(rvd, '%B,%d,%Y') - datetime.datetime.strptime(datev1 , '%Y-%m-%d')).days
                                    review_gap_lst.append(reviewgap)
                                total_time += (datetime.datetime.strptime(rvd, '%B,%d,%Y') - datetime.datetime.strptime(v_date , '%Y-%m-%d')).days
                                if author_cmt == 0 and author_check(reviews[doi][v2][r]["author"], authors):
                                    author_cmt = 1
                            dic[doi]["separated comment word count"] = dic[doi]["separated comment word count"][:-1] +"|"
                            review_gap_lst.sort()
                            for g in review_gap_lst:
                                dic[doi]["comment days since version 1"] += str(g) + ";"
                            dic[doi]["comment days since version 1"] = dic[doi]["comment days since version 1"][:-1] + "|"
                        if review_gap_lst == []:
                            dic[doi]["comment days since version 1"] += "|"
                        counter += len(reviews[doi][v2])
                dic[doi]["separated comment word count"] = dic[doi]["separated comment word count"][:-1]
                dic[doi]["comment days since version 1"] = dic[doi]["comment days since version 1"][:-1]
                dic[doi]["Comment number"] = counter
                dic[doi]["all comment word count"] = cmt_len
                if counter == 0:
                    dic[doi]["average comment day"] = 0
                else:
                    dic[doi]["average comment day"] = total_time / counter
                dic[doi]["has author comment"] = author_cmt
#community
                cmnt_dic = {"Faculty Opinions":0,
                            "Publons":0,
                            "PREreview":0,
                            "preLights":0,
                            "PubPeer":0,
                            "Rapid Reviews Infectious Diseases":0,
                            "Arcadia Science":0,
                            "Other":0,
                            "community days since version 1":""}
                if doi in community:
                    for v3 in community[doi]:
                        if datev1:
                            cmntgap=(datetime.datetime.strptime(community[doi][v3]["time"], '%Y-%m-%d') - datetime.datetime.strptime(datev1 , '%Y-%m-%d')).days
                            cmnt_dic["community days since version 1"] += str(cmntgap) + ";"
                        plat = community[doi][v3]["platform"]
                        if plat in cmnt_dic:
                            cmnt_dic[plat] += 1
                        else:
                            cmnt_dic["Other"] += 1
                cmnt_dic["community days since version 1"] = cmnt_dic["community days since version 1"][:-1]
                for pt in cmnt_dic:
                    if pt != "community days since version 1":
                        dic[doi]["community review of " + pt] = cmnt_dic[pt]
                    else:
                        dic[doi]["community days since version 1"] = cmnt_dic[pt]
#trip
                # if doi in trips:
                #     if published[doi] != "NA":
                #         trip_plt = trips[doi]
                #         if published[doi]["container-title"]:
                #             pub_plt = published[doi]["container-title"][0]
                #             if pub_plt not in trip_plt:
                #                 c2.append(doi)
                #             else:
                #                 cc += 1
    # print(c2)
                dic[doi]["TRiP words count"] = 0
                dic[doi]["TRiP link count"] = 0
                dic[doi]["TRiP link"] = ""
                dic[doi]["Published in TRiP journal"] = 0
                if doi in trips:
                    for p2 in trips[doi]:
                        out = 0
                        l = 0
                        li = ""
                        for tid in trips[doi][p2]:
                            if p2 in trip_text:
                                out += remove_stop_count(trips[doi][p2][tid]["content"])
                            if trips[doi][p2][tid]["pdf_link"]:
                                for pdf in trips[doi][p2][tid]["pdf_link"]:
                                    l += 1
                                    li = li + pdf + ";"
                            if trips[doi][p2][tid]["link"]:
                                for link in trips[doi][p2][tid]["link"]:
                                    l += 1
                                    li = li + link + ";"
                        dic[doi]["TRiP words count"] += out
                        dic[doi]["TRiP link count"] += l
                        dic[doi]["TRiP link"] += li
                        if published[doi] and published[doi] != "NA" and published[doi]["container-title"]:
                            if p2 in published[doi]["container-title"] or p2 == "EMBO Press":
                                dic[doi]["Published in TRiP journal"] = 1
                            elif p2 == "Peer Community In" and "Peer Community Journal" in published[doi]["container-title"] :
                                dic[doi]["Published in TRiP journal"] = 1
                        
#published
                pub_dic = {
                            "publication doi":"" ,
                            "publication date":"",
                            "publication journal or conference":"",
                            "IF journal 2019":0,
                            "publication reference count":0,
                            "publication citation count":0,
                            "publisher":""}
                if preprints[doi][v]["published"] != "NA":
                    pub_dic["publication doi"] = preprints[doi][v]["published"]
                if doi in published and published[doi] and published[doi] != "NA" :
                    date = published[doi]["date"]
                    pub_dic["publication date"] = date
                    pub_dic["publisher"] = published[doi]["publisher"]
                    if published[doi]["container-title"]:
                        pub_dic["publication journal or conference"] = published[doi]["container-title"][0]
                    else:
                        pub_dic["publication journal or conference"] = ""
                    pub_dic["publication reference count"] = published[doi]["reference-count"]
                    pub_dic["publication citation count"] = published[doi]["is-referenced-by-count"]
                    if published[doi]["container-title"]:
                        jnal = published[doi]["container-title"][0]
                        if jnal.lower() in ifd:
                            if ifd[jnal.lower()] != "nan":
                                pub_dic["IF journal 2019"] = ifd[jnal.lower()]
                        elif jnal in ifd2:
                            pub_dic["IF journal 2019"] = ifd2[jnal]
#makeup
                if pub_dic["publication doi"] == "" and doi in makeupdic and makeupdic[doi]:
                    pub_dic["publication doi"] = makeupdic[doi]["published-doi"]
                    pub_dic["publication date"] = makeupdic[doi]["date"]
                    if makeupdic[doi]["container-title"]:
                        pub_dic["publication journal or conference"] = makeupdic[doi]["container-title"][0]
                        jnal = makeupdic[doi]["container-title"][0]
                        if jnal.lower() in ifd:
                            if ifd[jnal.lower()] != "nan":
                                pub_dic["IF journal 2019"] = ifd[jnal.lower()]
                        elif jnal in ifd2:
                            pub_dic["IF journal 2019"] = ifd2[jnal]
                    pub_dic["publication reference count"] = makeupdic[doi]["reference-count"]
                    pub_dic["publication citation count"] = makeupdic[doi]["is-referenced-by-count"]
                    pub_dic["publisher"] = makeupdic[doi][ "publisher"]
                    
                for n in pub_dic:
                    dic[doi][n] = pub_dic[n]


            
    print("dictionary done!")
    total = len(dic)
    with open("0.7_preprint_dataset.csv","w",newline='') as f:
        writer = csv.writer(f)
        writer.writerow(dic[doi].keys())
        for doi in dic:
            writer.writerows([dic[doi].values()])
    print("total %d done!"%total)