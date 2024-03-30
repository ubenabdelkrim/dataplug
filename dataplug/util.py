from __future__ import annotations

import logging
import re
import os
import shutil

import botocore

from typing import Type, Any, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from dataplug import CloudObject

logger = logging.getLogger(__name__)

S3_PATH_REGEX = re.compile(r"^\w+://.+/.+$")


def setup_logging(level=logging.INFO):
    root_logger = logging.getLogger("dataplug")
    root_logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)


def split_s3_path(path):
    if not S3_PATH_REGEX.fullmatch(path):
        raise ValueError(f"Path must satisfy regex {S3_PATH_REGEX}")

    bucket, key = path.replace("s3://", "").split("/", 1)
    return bucket, key


def force_delete_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def head_object(s3client, bucket, key):
    metadata = {}
    try:
        head_res = s3client.head_object(Bucket=bucket, Key=key)
        del head_res["ResponseMetadata"]
        response = head_res
        if "Metadata" in head_res:
            metadata.update(head_res["Metadata"])
            del response["Metadata"]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            raise KeyError()
        else:
            raise e
    return response, metadata



def patch_object(cloud_object: CloudObject):
    head = cloud_object.storage.head_object(Bucket=cloud_object.meta_path.bucket, Key=cloud_object.meta_path.key)
    print(head)
    metadata = head.get("Metadata", {})
    print(metadata)
    attrs_bin = pickle.dumps(metadata)
    cloud_object.storage.put_object(
        Body=attrs_bin,
        Bucket=cloud_object._attrs_path.bucket,
        Key=cloud_object._attrs_path.key,
        Metadata={"dataplug": "dev"},
    )
    cloud_object.fetch()
