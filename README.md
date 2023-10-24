# PDF Filler

The VoteAmerica PDF Filler is a Lambda function that wraps PDFTK to fill in PDF forms and stamp signatures onto PDFs.

## Usage

The PDF Filler is a single Lambda function that can be invoked with the following payload
```js
{
  "template": {
    "pdf": "...", // base64-encoded PDF
    "is_form": true,
    "flatten_form": true,
    "signature_locations": {
      "1": { // Page number
        "x": 1,
        "y": 2,
        "width": 3,
        "height": 4
      }
    }
  },
  "data": {
    // key-value pairs
  },
  "signature": "...", // presigned URL of the signature
  "output": "...", // presigned PUT URL for the result PDF
}
```

You can see an example of calling this in `utils/test.py`.

## PDFTK

This repo includes the prebuilt pdftk binary from the pdftk-java
project: https://gitlab.com/pdftk-java

## Deployment

This project uses the Serverless framework to deploy an AWS CloudFormation stack. The primary resource in the 
stack is the Lambda function itself.

To deploy, first make sure you have packages installed by running the following:
```bash
pipenv install
npm install
yarn install
```

Your local version of Pipenv and Node could affect your ability to successfully run the deployment process.
A combination of Pipenv version 2022.5.2 and Node version 14.21.3 should work.

Make sure your local Docker daemon is running. 

Then, run: 
```bash
sls deploy --stage {stage}
```

Possible stages include: local, dev, prod
