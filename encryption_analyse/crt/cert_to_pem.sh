#!/bin/bash

# Set folder path
FOLDER_PATH="/home/sider/Desktop/Data/cert"

# Set filename
CERT_FILE_NAME="cert.cer"
CRT_FILE_NAME="cert.crt"
PEM_FILE_NAME="cert.pem"

cd "$FOLDER_PATH"

# Check if the cert.cer file exists
if [ -f "$CERT_FILE_NAME" ]; then
    # Convert certificate in DER format to CRT format
    openssl x509 -inform DER -in "$CERT_FILE_NAME" -out "$CRT_FILE_NAME"
    
    # Check if conversion is successful
    if [ $? -eq 0 ]; then
        # Convert certificate in CRT format to PEM format
        openssl x509 -in "$CRT_FILE_NAME" -out "$PEM_FILE_NAME" -outform PEM
        echo "The conversion is completed and the PEM file has been generated."
    else
        echo "Conversion to CRT format failed."
    fi
else
    echo "The file specified $CERT_FILE_NAME does not exist."
fi

# sudo rm -rf $CERT_FILE_NAME
# sudo rm -rf $CRT_FILE_NAME
