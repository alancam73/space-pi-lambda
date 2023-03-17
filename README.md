# space-pi-lambda
Lambda using AWS Rekognition to detect PIes in Space for Pi Day

![Screenshot 2023-03-17 133948_50x50](https://user-images.githubusercontent.com/57327440/226038582-437a0604-8cd9-4532-ab95-55893f9528e5.png "Space PI website")


## Overview
Lambda which uses AWS Rekognition to detect PIes in Space images for PI Day.
Pushes the result image-name and associated pie-count to a file
so that an S3 static website (with CloudFront) can then leverage the data
Note : the Lambda is configured with ~6 mins as the timeout because starting 
the model can take almost 5 mins (stopping the model, which is done at the end,
is much, much quicker)


## Dependent Repositories
To complete the picture you also need: -

https://github.com/alancam73/xyzfillin - S3 Static Website with CloudFront doing slideshow of images with (or without!) pies!


## Pre-requisites
* python 3.8 or higher
* IAM permissions - the Lambda needs access to S3, Rekognition, and CloudWatch logs
  * Hence import the following Managed policies (NOTE - more restrictive policies can also be used)
     * AmazonRekognitionFullAccess
     * AmazonS3FullAccess
     * AWSLambdaBasicExecutionRole
* Configuration - timeout of >= 6 minutes (since it takes ~5 mins to start the model inference)


## Environment variables
Key           | Value
------------- | -------------
bucket_name   | Name of the bucket with the images/ and the index.html and slideshow.js
model_arn     | ARN of the Reko model generated
project_arn   | ARN of the project containing the Reko model
version_name  | Version name/number of the Reko model

	          
## Outputs
* Creates a file images.txt with the following format which the space-pi static website ingests: -
```
images/021518_LG_space-beauty_main.jpg,0
images/0302063_medium.jpg,1
images/PIA18033_medium.jpg,0
images/PIA19821_medium.jpg,1
images/Space_night_sky.jpg,1
images/archives_casa_wuutar.jpg,2
```
The number at the end of each row is the number of PIes Rekognition detected in that image

	       
## Model generation
[Amazon Rekognition](https://aws.amazon.com/rekognition/) is straightforward to use. 
1. First, we create a dataset - uploaded images (20+) of Space with transparent PIes overlaid
2. Then we label the images by drawing a bounding box around the pie(s)
3. Next, we train the model using a standard 80/20 Training/Test split
4. Finally, we check the performance metrics (F1 score etc) to assure model accuracy

After this is complete we invoke the Reko Model via our Lambda function (boto3 Python SDK)

NOTE : be sure to stop the model at the end of the Lambda to avoid unneceesary charges!
