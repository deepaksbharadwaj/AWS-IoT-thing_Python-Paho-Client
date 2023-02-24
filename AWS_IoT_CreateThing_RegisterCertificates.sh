#!/bin/bash
# Author - Deepak Sridhar Bharadwaj - Working code 20 Feb 2023
# Above bash script is used to automatically create and configure an IoT Device 
# Script creates the certificates, primary and public keys and registers this newly created device on the AWS IoT core.

# assign the thing name to a shell variable 
THING_NAME=ESA_SOA_TestDevice03

# create the thing in the AWS IoT Core device registry 
aws iot create-thing --thing-name $THING_NAME 
echo "THING_NAME : " $THING_NAME 

# list current things
aws iot list-things --output table
# list current policies
aws iot list-policies --output table

export IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)
echo "IOT_ENDPOINT : " $IOT_ENDPOINT

# crete and register the device certificate with AWS IoT Core 
aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile $THING_NAME.certificate.pem \
--public-key-outfile $THING_NAME.publicKey.pem --private-key-outfile $THING_NAME.privkey.pem  > register_certificate.json

CERTIFICATE_ARN=$(jq -r ".certificateArn" register_certificate.json)
CERTIFICATE_ID=$(jq -r ".certificateId" register_certificate.json)

echo "CERTIFICATE_ARN : " $CERTIFICATE_ARN
echo "CERTIFICATE_ID : " $CERTIFICATE_ID

# create an IoT policy 
POLICY_NAME=${THING_NAME}_Policy
aws iot create-policy --policy-name $POLICY_NAME \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action": "iot:*","Resource":"*"}]}'
  
echo "POLICY_NAME : " $POLICY_NAME
 
# attach the policy to your certificate
#aws iot attach-policy --policy-name $POLICY_NAME --target $CERTIFICATE_ARN 
aws iot attach-principal-policy --principal $CERTIFICATE_ARN  --policy-name $POLICY_NAME

# attach the certificate to your thing
aws iot attach-thing-principal --thing-name $THING_NAME --principal $CERTIFICATE_ARN


echo "Press any key to continue" 
while [ true ] ; do
	read -t 3 -n 1
if [ $? = 0 ] ; then
	exit ;
else
	echo "waiting for the keypress"
fi
done