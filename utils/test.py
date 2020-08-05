import sys
import os
import boto3
import base64
import json

utils_dir = os.path.dirname(__file__)

BUCKET = os.environ["S3_BUCKET"]
PREFIX = os.environ["S3_PREFIX"]

s3_client = boto3.client("s3")
lambda_client = boto3.client("lambda")

sig_url = s3_client.generate_presigned_url(
    "get_object", Params={"Bucket": BUCKET, "Key": f"{PREFIX}/sig.jpeg"}
)

output_url = s3_client.generate_presigned_url(
    "put_object", Params={"Bucket": BUCKET, "Key": f"{PREFIX}/out.pdf"}
)


def read_pdf(relpath):
    abspath = os.path.join(utils_dir, relpath)
    with open(abspath, "rb") as f:
        return base64.b64encode(f.read()).decode()


s3_client.upload_file(os.path.join(utils_dir, "sig.jpeg"), BUCKET, f"{PREFIX}/sig.jpeg")


lambda_payload = {
    "template": [
        {
            "pdf": read_pdf("test-input-page-1.pdf"),
            "is_form": True,
            "flatten_form": True,
        },
        {
            "pdf": read_pdf("test-input-page-2-3.pdf"),
            "is_form": True,
            "signature_locations": {
                "1": {"x": 300, "y": 490, "width": 200, "height": 28}
            },
        },
        {
            "pdf": read_pdf("test-input-page-4.pdf"),
            "signature_locations": {
                "1": {"x": 188, "y": 50, "width": 200, "height": 28}
            },
        },
    ],
    "data": {
        "is_18_or_over": True,
        "title_mr": False,
        "title_ms": True,
        "first_name": "Foo",
        "last_name": "Bar",
        "address1": "None",
        "zipcode": None,
        "mailto_line_1": "some address!",
    },
    "signature": sig_url,
    "output": output_url,
}

response = lambda_client.invoke(
    FunctionName="pdf-filler-local-fill",
    InvocationType="RequestResponse",
    LogType="Tail",
    Payload=bytes(json.dumps(lambda_payload), "utf-8"),
)

print("RESPONSE:")
print(response["Payload"].read())

print("LOGS:")
print(base64.b64decode(response["LogResult"]).decode())

if response.get("FunctionError"):
    print(f"FUNCTION FAILED: {response['FunctionError']}")
else:
    print("RESULT:")
    print(
        s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": BUCKET, "Key": f"{PREFIX}/out.pdf"}
        )
    )

