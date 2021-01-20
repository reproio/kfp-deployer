# kfp-deployer

Deploy your ml-pipeline with `kfp-deploy` from cli.

## How to use

`kfp-deploy https://your-kubeflow-host/ "pipeline-name" ./pipeline_file.yaml`

for more detail, see `kfp-deploy -h`.

## what the difference from `kfp pipeline upload`?


Kubeflow Pipelines requires the all pipelines must have unique names. 
Otherwise you have to use `update the version` instead of `upload the pipeline`.
Furthermore, you have to use unique name when uploading the new version of pipeline.

This command does everything required in the upload process for you. 
This command will communicate with kfp host and automatically determine 
whether update or upload is required and perform it.
Furthermore, the version string is automatically generated based on the upload timestamp.
