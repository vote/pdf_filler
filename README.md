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
