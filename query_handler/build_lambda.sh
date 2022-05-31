#!/bin/bash

ZIPFILE="`pwd`/lambda.zip"

echo $ZIPFILE

rm -f $ZIPFILE
cd lambda
zip $ZIPFILE *.py
cd env/lib/python3.9/site-packages
zip -r $ZIPFILE *