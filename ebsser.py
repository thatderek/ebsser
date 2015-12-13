#/usr/bin/python

import boto3
import pprint
import time
import datetime
import zipfile
import os

accountNumber = boto3.client('iam').list_roles()['Roles'][0]['Arn'].split(":")[4]

def createStack(stackName, stackDict):
    cfClient = boto3.client('cloudformation')
    resp = cfClient.create_stack(
            StackName=stackName,
            TemplateBody=stackDict[stackName],
            Capabilities=["CAPABILITY_IAM"]
            )
    return resp['StackId']

def updateStack(stackName, stackDict): 
    cfClient = boto3.client('cloudformation') 
    resp = cfClient.update_stack(
            StackName=stackName, 
            TemplateBody=stackDict[stackName]
            )

    return resp['StackId']

def stackStatus(stackId):
    cfClient = boto3.client('cloudformation')
    stacks = cfClient.list_stacks()
    for stack in stacks['StackSummaries']:
        if stack['StackId'] == stackId:
            if stack['StackStatus'] != 'CREATE_COMPLETE':
                print "Stack creation not done. Waiting 10 seconds to try again."
                time.sleep(10)
                stackStatus(stackId)
            else:
                "Stack creation done. Moving on."
                return 

def stackCheck(stackName, stackList, stackDict):
    if stackName in stackList: 
        print "stack " + stackName + " exists. Updating" 
        return updateStack(stackName, stackDict)
    else:
        print "creating stack " + stackName 
        return createStack(stackName, stackDict)

def zipIt(path):
    with zipfile.ZipFile(path + '.zip', 'w') as zipped:
        zipped.write(path)

def main():

    cfClient = boto3.client('cloudformation')
    
    cfStacks = {}
    s3StackName = 'ebsserS3'
    lambdaStackName = 'ebsserLambda'

    with open ("cft/s3cft.json", "r") as datafile:
        cfStacks[s3StackName] = datafile.read()

    with open("cft/lambda.json", "r") as lamdaStackFile:
        cfStacks[lambdaStackName] = lamdaStackFile.read()
    
    lsCftResp = cfClient.list_stacks(
                StackStatusFilter=[
                    'CREATE_IN_PROGRESS',
                    'CREATE_FAILED',
                    'CREATE_COMPLETE',
                    'ROLLBACK_IN_PROGRESS',
                    'ROLLBACK_FAILED',
                    'ROLLBACK_COMPLETE',
                    'DELETE_IN_PROGRESS',
                    'DELETE_FAILED',
                    'UPDATE_IN_PROGRESS',
                    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                    'UPDATE_COMPLETE',
                    'UPDATE_ROLLBACK_IN_PROGRESS',
                    'UPDATE_ROLLBACK_FAILED',
                    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                    'UPDATE_ROLLBACK_COMPLETE'
                    ]
            )

    pprint.pprint(lsCftResp)
    
    stackNames = []
    for stack in lsCftResp['StackSummaries']:
        if stack['StackStatus'] != 'DELETE_COMPLTETE':
            stackNames.append(stack['StackName'])


    stackId = stackCheck(s3StackName, stackNames, cfStacks)

   
    stackStatus(stackId)
    
    s3Client = boto3.resource('s3')

    os.chdir("./python")

    for codeFile in os.listdir("."):
        if codeFile.endswith(".py"):
            zipIt(codeFile)
    os.chdir("..")
    for zipFile in os.listdir("./python"):
        if zipFile.endswith(".zip"):
            s3Client.meta.client.upload_file("./python/"+zipFile, accountNumber+"-ebsser", zipFile)

    stackId = stackCheck(lambdaStackName, stackNames, cfStacks)
    stackStatus(stackId)


    print "got here. Woot"






    


if __name__ == '__main__':
    main()
