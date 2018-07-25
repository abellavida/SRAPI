import urllib.request
import urllib.parse
import json
from pprint import pprint
import pymongo
from pymongo import MongoClient
import csv
import requests
from config import db, dbtemp

##import requests

def SR_Get(api_key):
        header = {"X-SmartToken":'%s' %api_key, 'Content-Type': 'application/json; charset=utf-8'}
##        url='https://api.smartrecruiters.com/jobs/7303b8cd-d439-4fe7-a029-50a6d9c042c4'
##        url='https://api.smartrecruiters.com/jobs'
##      url='https://api.smartrecruiters.com/user-api/v201804/access-groups'
        url = 'https://api.smartrecruiters.com/configuration/job-properties'
        
        res = urllib.request.Request(url=url, headers=header, method='GET')
        res_open = urllib.request.urlopen(res, timeout=10)
        res_body = res_open.read()       
        j=json.loads(res_body.decode("utf-8"))
        
##        client = MongoClient()
##        db = client.srapi
        job_properties = db.job_properties.insert_one(j)
##        dbtemp  = client.temp
        result = db.new_srapi_data.insert_one(j)
      
        cursor = db.new_srapi_data.distinct("content")
##        pprint(cursor)

        for content in cursor:
##                print(content, '/n')
                cid = content['id']
                label = content['label']
                url2 = ('https://api.smartrecruiters.com//configuration/job-properties/%s/values' %cid)

                res2 = urllib.request.Request(url=url2, headers=header, method='GET')
                res_open2 = urllib.request.urlopen(res2, timeout=10)
                res_body2 = res_open2.read()       
                j2=json.loads(res_body2.decode("utf-8"))
##                pprint(j2)
                jobprop = {'jobprop' : cid, 'jobprop_label': label}
                j3={}
                j3=jobprop.copy()
                jpvals = []
                
                try:
##                        print (next (item for item in j2 if j2['content'][0]['label'] != None))
                        for l in j2['content']:
##                                print(l['label'])
                                jpID = l['id']
                                jpLabel = l['label']
                                jpvals.append({'id' : jpID, 'label' :  jpLabel})
##                                print ("JPVals: ", jpvals)
                except IndexError:
                        continue
##                print ("JPVals: ", jpvals)
                j3.update({ 'jpvals' : jpvals})
                j2['content'].append(jobprop)

##                pprint(j3)

                db.job_prop_values.insert_one(j2)
                db.jpvs_new.insert_one(j3)

        db.new_srapi_data.delete_many({})


def SR_Post(api_key):

   
##        url='https://api.smartrecruiters.com//configuration//job-properties//{id}//values//{valueId}//dependents//{dependentId}//values'

##        data_len = len(data)
##        print('Content Length :', data_len)

    client = MongoClient()
    db = client.srapi

    with open('//home//jc//SRAPI//Data//job_field_dependencies.csv') as j:

        jfd = csv.reader(j)
        next (jfd)
        for i in jfd:
            parent = i[0]
            child = i[1]
    ##        print (parent, " ", child)
            jobprop = []
            label = []
            valueId = []
            depId = []

            value = db.job_prop_values.find_one({'content.label': parent})
            x = value['content']
            v = 0
    ##        print(x)
            while v < 1000:
                try:
                    if parent == x[v]['label']:
    ##                    print ('Match: ', x[v]['id'], ' ', x[4]['jobprop'])
                        valueId = x[v]['id']
                        jobprop = x[4]['jobprop']
                    v += 1
                except KeyError:
                    v += 1
                    next
                except IndexError:
                    v += 1
                    next


            value = db.job_prop_values.find_one({'content.label': child})
            d = value['content']
    ##        print('child: ', child)
            n = 0
            while n < 1000:
                try: 
                    if child == d[n]['label']:
    ##                    print('Match: ', d[n]['id'])
                        depId = d[n]['id']
                    n +=1
                except KeyError:
                    n +=1
                    next
                except IndexError:
                    n +=1
                    next

            url = ('https://api.smartrecruiters.com//configuration//job-properties//%s//values//%s//dependents//%s//values' %(jobprop, valueId, depId))
            print(url, '\n')

            jp_dep = {
                                  "id": depId
                                }
##            jp_dep = urllib.parse.urlencode(jp_dep).encode('utf-8')
            print(json.dumps(jp_dep))
            clen = str(len(jp_dep))

            header = {"X-SmartToken":'%s' %api_key, 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': clen}
##            res_body = []
##            content = []
##
##            req = urllib.request.Request(url, data=json.dumps(jp_dep), headers=header, method="POST")
##            res, content = urllib.request.urlopen(req, timeout=10)
##            res_body= res.read()
##            print(content)

            r= requests.post(url, headers = header, data=json.dumps(jp_dep))
            print(r.json(), '\n')
            return r

def SR_Delete():
##        client = MongoClient()
##        db = client.srapi
##        dbtemp = client.temp

        delete_jp = db.job_properties.delete_many({})
        delete_jpv=db.job_prop_values.delete_many({})
        delete_new_srdata= db.new_srapi_data.delete_many({})
        delete_jpv_new = db.jpvs_new.delete_many({})


        
if __name__ == "__main__":
                api_key = input('AP Key: ')
                
                SR_Get(api_key)
##                SR_Post(api_key)

               
