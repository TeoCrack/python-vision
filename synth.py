# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
from synthtool import gcp
from synthtool.languages import python

gapic = gcp.GAPICBazel()
common = gcp.CommonTemplates()
versions = ["v1", "v1p1beta1", "v1p2beta1", "v1p3beta1", "v1p4beta1"]


# ----------------------------------------------------------------------------
# Generate vision GAPIC layer
# ----------------------------------------------------------------------------
for version in versions:
    library = gapic.py_library(
        service="vision",
        version=version,
        bazel_target=f"//google/cloud/vision/{version}:vision-{version}-py",
        include_protos=True
    )

    s.move(library / f"google/cloud/vision_{version}/proto")
    s.move(library / f"google/cloud/vision_{version}/services")
    s.move(library / f"google/cloud/vision_{version}/types")
    s.move(library / f"google/cloud/vision_{version}/__init__.py")
    s.move(library / f"google/cloud/vision_{version}/py.typed")
    s.move(library / f"tests/unit/gapic/vision_{version}")

    if version == "v1":
        s.move(library / "google/cloud/vision")

    # don't publish docs for these versions
    if version not in ["v1p1beta1"]:
        s.move(library / f"docs/vision_{version}")

    # Add vision helpers to each version
    s.replace(
        f"google/cloud/vision_{version}/__init__.py",
        "from .services.image_annotator import ImageAnnotatorClient",
        "from google.cloud.vision_helpers.decorators import "
        "add_single_feature_methods\n"
        "from google.cloud.vision_helpers import VisionHelpers\n\n"
        "from .services.image_annotator import ImageAnnotatorClient as IacImageAnnotatorClient",
    )

    s.replace(
        f"google/cloud/vision_{version}/__init__.py",
        "__all__ = \(",
        "@add_single_feature_methods\n"
        "class ImageAnnotatorClient(VisionHelpers, IacImageAnnotatorClient):\n"
        "\t__doc__ = IacImageAnnotatorClient.__doc__\n"
        "\tFeature = Feature\n\n"
        "__all__ = (",
    )

    # Temporary workaround due to bug https://github.com/googleapis/proto-plus-python/issues/135
    s.replace(
        f"google/cloud/vision_{version}/services/image_annotator/client.py",
        "request = image_annotator.BatchAnnotateImagesRequest\(request\)",
        "request = image_annotator.BatchAnnotateImagesRequest(request)\n"
        "            if requests is not None:\n"
        "                for i in range(len(requests)):\n"
        "                    requests[i] = image_annotator.AnnotateImageRequest(requests[i])"
    )
    s.replace(
        f"google/cloud/vision_{version}/services/image_annotator/client.py",
        "request = image_annotator.BatchAnnotateFilesRequest\(request\)",
        "request = image_annotator.BatchAnnotateFilesRequest(request)\n"
        "            if requests is not None:\n"
        "                for i in range(len(requests)):\n"
        "                    requests[i] = image_annotator.AnnotateFileRequest(requests[i])"
    )
    s.replace(
        f"google/cloud/vision_{version}/services/image_annotator/client.py",
        "request = image_annotator.AsyncBatchAnnotateImagesRequest\(request\)",
        "request = image_annotator.AsyncBatchAnnotateImagesRequest(request)\n"
        "            if requests is not None:\n"
        "                for i in range(len(requests)):\n"
        "                    requests[i] = image_annotator.AnnotateImageRequest(requests[i])"
    )
    s.replace(
        f"google/cloud/vision_{version}/services/image_annotator/client.py",
        "request = image_annotator.AsyncBatchAnnotateFilesRequest\(request\)",
        "request = image_annotator.AsyncBatchAnnotateFilesRequest(request)\n"
        "            if requests is not None:\n"
        "                for i in range(len(requests)):\n"
        "                    requests[i] = image_annotator.AsyncAnnotateFileRequest(requests[i])"
    )

s.replace(
    "google/cloud/vision/__init__.py",
    "from google.cloud.vision_v1.services.image_annotator.client import ImageAnnotatorClient",
    "from google.cloud.vision_v1 import ImageAnnotatorClient"
)

# Move docs configuration
s.move(library / f"docs/conf.py")

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
   samples=True,
   microgenerator=True,
   cov_level=98,
   system_test_external_dependencies=["google-cloud-storage"]
)
s.move(templated_files, excludes=[".coveragerc"])  # microgenerator has a good .coveragerc file

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------
python.py_samples(skip_readmes=True)

# TODO(busunkim): Use latest sphinx after microgenerator transition
s.replace("noxfile.py", """['"]sphinx['"]""", '"sphinx<3.0.0"')

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
