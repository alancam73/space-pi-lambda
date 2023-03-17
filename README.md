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

	          
	        
	       
