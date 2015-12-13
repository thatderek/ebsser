# ebsser
This is a python script that creates a cloudformation stack to backup all ebs volumes in an aws account. 

***instructions***

Clone this repo locally. From the base folder, run `python ebsser.py`. After the script completes a lambda scheduled event must be created to trigger the backup. Learn more about [Scheduled Events Here](http://docs.aws.amazon.com/lambda/latest/dg/with-scheduled-events.html) 
> Note: As of December 2015, a Lambda Scheduled Event cannot be created via the api or a cloudformation template. When Amazon adds the ability to do so, this tool will be updated. 

Requirements:
* local machine with python2.7 and boto3 library
* aws account with admin rights
* aws cli and [configured credentials file](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)

***v 0.1.0***
