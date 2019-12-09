#!/usr/bin/env bash

sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket mbrenner-aws-serverless-template
sam deploy --template-file packaged.yaml --stack-name items --capabilities CAPABILITY_IAM
