#
# Lambda which uses AWS Rekognition to detect pies in Space images.
# Pushes the result image-name and associated pie-count to a file
# so that an S3 static website (with CloudFront) can then leverage the data
# Note : the Lambda is configured with ~6 mins as the timeout because starting 
# the model can take almost 5 mins (stopping the model, which is done at the end,
# is much, much quicker)
#

from __future__ import with_statement
import boto3
import json
import logging
import os
from botocore.exceptions import ClientError
import argparse



s3_client = boto3.client('s3')


# Rekognition functions
# Start the Reko model for pie detection
def start_model(project_arn, model_arn, version_name, min_inference_units):

    client=boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
            VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage']) 
    except Exception as e:
        print(e)
        
    print('Done...')


# detect pies
def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)

    return len(response['CustomLabels'])


# stop the Reko model
def stop_model(model_arn):

    client=boto3.client('rekognition')

    print('Stopping model:' + model_arn)

    #Stop the model
    try:
        response=client.stop_project_version(ProjectVersionArn=model_arn)
        status=response['Status']
        print ('Status: ' + status)
    except Exception as e:  
        print(e)  

    print('Done...')
    

# S3 functions
# upload file to S3
def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# main lambda function handler
def lambda_handler(event, context):
   
   args = None
   project_arn = None
   model_arn = None
   version_name = None
   bucket_name = None
   
   # allow local Python execution testing as well as Lambda env
   execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
   if execEnv.startswith("AWS_Lambda"):
      print("In Lambda context...")
      project_arn = str(os.getenv('project_arn'))
      model_arn = str(os.getenv('model_arn'))
      version_name = str(os.getenv('version_name'))
      bucket_name = str(os.getenv('bucket_name'))
   else:
      print("In Python context...")
      parser = argparse.ArgumentParser()
 
      # Adding positional arguments
      parser.add_argument("project_arn", help = "Project ARN for the Reko model")
      parser.add_argument("model_arn", help = "Model ARN for the Reko model")
      parser.add_argument("version_name", help = "Reko model version")
      parser.add_argument("bucket_name", help = "S3 bucket with our images")
        
      args = parser.parse_args()
      project_arn = args.project_arn
      model_arn = args.model_arn
      version_name = args.version_name
      bucket_name = args.bucket_name
      
        
   print ("project_arn: ", project_arn)
   print ("model_arn: ", model_arn)
   print ("version_name: ", version_name)
   print ("bucket_name: ", bucket_name)
    
   min_inference_units=1 
   start_model(project_arn, model_arn, version_name, min_inference_units)
   
   objects = s3_client.list_objects_v2(Bucket=bucket_name,
                                       Prefix='images/')
   
   img=''
   min_confidence=50    # we didnt use much training data so use lo confidence threshold

   f = open("/tmp/images.txt", "w")

   for obj in objects['Contents']:
#      print(obj['Key'])

      img = obj['Key']
      label_count=show_custom_labels(model_arn, bucket_name, img, min_confidence)
      print("Custom labels detected: " + str(label_count))

      img_reko = ''
      img_reko = obj['Key'] + ',' + str(label_count) + '\n'
      print(img_reko)

      f.write(img_reko)

   f.close()
   
   # upload file of image-name & associated pie-count to S3 bucket
   upload_file("/tmp/images.txt", bucket_name, "images.txt")
   
   stop_model(model_arn)
   
   return None       


# allow local Python execution testing
if __name__ == '__main__':
    lambda_handler(None,None)

