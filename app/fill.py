import base64
import os
import random
import string
import tempfile
from io import BytesIO
from typing import Any, Dict, Optional

import requests
from pdf_template import (  # type:ignore
    PDFTemplate,
    PDFTemplateSection,
    SignatureBoundingBox,
)
from PIL import Image  # type:ignore
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "PUT"],
    backoff_factor=1,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


# Add our bin/ folder to PATH
os.environ[
    "PATH"
] = f"{os.environ.get('PATH', '')}:{os.path.join(os.path.dirname(__file__))}/../bin/"


def random_name(length=32) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


def load_signature_locations(
    locations_json: Optional[Dict[str, Any]]
) -> Optional[Dict[int, SignatureBoundingBox]]:
    if not locations_json:
        return None

    signature_locations = {}
    for k, v in locations_json.items():
        signature_locations[int(k)] = SignatureBoundingBox(**v)

    return signature_locations


def load_template_section(
    section_json: Dict[str, Any], tmpdir: str
) -> PDFTemplateSection:
    # Write the PDF to disk and swap in the path to that file
    pdf_path = os.path.join(tmpdir, random_name())
    pdf_bytes = base64.b64decode(section_json["pdf"], validate=True)
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    return PDFTemplateSection(
        path=pdf_path,
        is_form=section_json.get("is_form", False),
        flatten_form=section_json.get("flatten_form", True),
        signature_locations=load_signature_locations(
            section_json.get("signature_locations", None)
        ),
    )


def handler(event: Any, context: Any):
    # Create a tmpdir for writing the intermediate PDFs to
    with tempfile.TemporaryDirectory() as tmpdir:
        output_url = event["output"]

        # Load signature
        signature = None
        signature_url = event.get("signature")
        if signature_url:
            sig_response = http.get(signature_url)
            sig_response.raise_for_status()
            signature = Image.open(BytesIO(sig_response.content))

        # Load data
        data = event.get("data", {})

        # Load template
        template = PDFTemplate(
            [
                load_template_section(section_json, tmpdir)
                for section_json in event["template"]
            ]
        )

        with template.fill(data, signature) as filled_pdf:
            res = http.put(url=output_url, data=filled_pdf)

            res.raise_for_status()

    return {"ok": True}
