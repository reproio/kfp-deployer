#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime
from typing import Optional
from pytz import timezone
import kfp

LIST_PAGE_SIZE = 1000

KNOWN_TIMEZONE_TABLE = {"JST": "Asia/Tokyo"}


def main() -> None:
    """Entrypoint."""
    parser = _build_argparser()
    args = parser.parse_args()
    deploy_pipeline(
        args.deploy_target_host, args.pipeline_name, args.pipeline_file, args.timezone
    )


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("deploy_target_host", type=str)
    parser.add_argument("pipeline_name", type=str)
    parser.add_argument("pipeline_file", type=str)
    parser.add_argument("-t", "--timezone", type=str, default="UTC")
    return parser


def deploy_pipeline(
    deploy_target_host: str, pipeline_name: str, pipeline_file_path: str, timezone: str
) -> None:
    # instantiate the kubeflow client
    client = kfp.Client(deploy_target_host)
    print("we will deploy into {}...".format(deploy_target_host))
    print("fetching existing pipeline...")
    pipeline_id = get_pipeline_id(client, pipeline_name)
    if pipeline_id is not None:
        print(f"pipeline {pipeline_name} is already exists by id: {pipeline_id}")
        print("-> deploying new version...")
        # upload new *version*
        version_str = create_version_str(pipeline_name, timezone)
        deployed_version_id = deploy_new_version(
            client, pipeline_id, pipeline_file_path, version_str
        )
        print("deployed new version in pipeline ID {}:".format(pipeline_id))
        print("  version ID: {}:".format(deployed_version_id))
    else:
        print(f"pipeline {pipeline_name} is not existed yet.")
        print("-> deploying new pipeline...")
        # upload new *pipeline*
        deployed_pipeline_id = deploy_new_pipeline(
            client, pipeline_name, pipeline_file_path
        )
        print("deployed new pipeline ID {}:".format(deployed_pipeline_id))


def get_pipeline_id(client: kfp.Client, pipeline_name: str) -> Optional[str]:
    """Get pipeline ID if that is already deployed.

    Args:
        client (kfp.Client): kfp client
        pipeline_name (str): name of pipeline

    Returns:
        Optional[str]: If found, return Pipeline ID. If not, return None.
    """
    pipelines_list = client.list_pipelines(page_size=LIST_PAGE_SIZE)
    if pipelines_list.pipelines:
        # check pipelines_list.pipelines is not null
        for p in pipelines_list.pipelines:
            if p.name == pipeline_name:
                # found
                return p.id
    # not found
    return None


def deploy_new_pipeline(
    client: kfp.Client, pipeline_name: str, pipeline_file_path: str
) -> str:
    """Deploy the new pipeline into kubeflow pipelines.

    Args:
        client (kfp.Client): kfp client
        pipeline_name (str): name of the pipeline
        pipeline_file_path (str): upload pipeline file

    Returns:
        str: generated pipeline ID
    """
    result = client.pipeline_uploads.upload_pipeline(
        pipeline_file_path, name=pipeline_name
    )
    return result.id


def deploy_new_version(
    client: kfp.Client, pipeline_id: str, pipeline_file_path: str, version_name: str
) -> str:
    """Deploy the new version of specified pipeline into kubeflow pipelines.

    Args:
        client (kfp.Client): kfp client
        pipeline_id (str): ID of pipeline that deploy into.
        pipeline_file_path (str): upload pipeline file
        version_name (str): version string of pipeline. must be unique in the pipeline.

    Returns:
        str: deployed version id
    """
    result = client.pipeline_uploads.upload_pipeline_version(
        pipeline_file_path, pipelineid=pipeline_id, name=version_name
    )
    return result.id


def create_version_str(
    pipeline_name: str,
    tz_name: str,
    timestamp: datetime = datetime.now(),
) -> str:
    """Create version string based on the local time.

    Args:
        pipeline_name (str): base version name.
        tz_name (str): name of timezone, like "UTC", "JST".

    Returns:
        str: generated version name.
    """
    if tz_name in KNOWN_TIMEZONE_TABLE:
        tz_name = KNOWN_TIMEZONE_TABLE[tz_name]
    now = timestamp.astimezone(timezone(tz_name))
    return f"{pipeline_name}-v{now:%y%m%d}-{now:%H%M%S}"


if __name__ == "__main__":
    main()