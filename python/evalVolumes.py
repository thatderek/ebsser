#!/usr/bin/python

import boto3
import pprint
import datetime

regions = ['ap-northeast-1', 
        'ap-southeast-1', 
        'ap-southeast-2', 
        'eu-central-1', 
        'eu-west-1', 
        'sa-east-1', 
        'us-east-1', 
        'us-west-1', 
        'us-west-2']

def getAccountId():
    return boto3.client('iam').get_user()['User']['Arn'].split(':')[4]

def getVols(region):
    client = boto3.client('ec2', region_name=region)
    return client.describe_volumes(DryRun=False)
   
def getSnaps(region):
    client = boto3.client('ec2', region_name=region)
    return client.describe_snapshots(DryRun=False,
            OwnerIds=[getAccountId()])

def makeSnap(region, volumeList): 
    client = boto3.client('ec2', region_name=region)
    for v in volumeList:
        print("Creating snapshot of " + v + " in region " + region)
        client.create_snapshot(
                VolumeId=v,
                Description="Automatically snapshotted by github.com/thatderek/ebsser"
                )


def lambdaWrapper(jsonPayload, context):
    main()

def main():
    pp = pprint.PrettyPrinter(indent=2)

    volList = {}

    for r in regions: 
        volResp = getVols(r)
        snapResp = getSnaps(r)
        
        tempVolList = []
        for v in volResp['Volumes']:
            tempVolList.append(v['VolumeId'])
            
            for s in snapResp['Snapshots']:
                
                if s['VolumeId'] == v['VolumeId']:
                    if datetime.datetime.strptime(str(s['StartTime'])[:-6], '%Y-%m-%d %H:%M:%S') > (datetime.datetime.today() + datetime.timedelta(-1)):
                        tempVolList.remove(v['VolumeId'])
        
        if len(tempVolList) > 0: 
            volList[r] = tempVolList
    
    for r in volList.keys():
        makeSnap(r, volList[r]) 

    pprint.pprint(volList)

if __name__ == '__main__':
    main()
