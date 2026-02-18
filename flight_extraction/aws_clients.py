# aws_clients.py
import boto3

REGION = "ap-south-1"

textract = boto3.client("textract", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
