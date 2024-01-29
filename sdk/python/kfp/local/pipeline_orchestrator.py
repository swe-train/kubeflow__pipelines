# Copyright 2024 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Code for locally executing a compiled pipeline."""
import logging
from typing import Any, Dict, Optional

from kfp.local import config
from kfp.local import dag_orchestrator
from kfp.local import io
from kfp.local import logging_utils
from kfp.local import placeholder_utils
from kfp.local import status
from kfp.local import utils
from kfp.pipeline_spec import pipeline_spec_pb2


def run_local_pipeline(
    pipeline_spec: pipeline_spec_pb2.PipelineSpec,
    arguments: Dict[str, Any],
) -> Dict[str, Any]:
    """kfp.local's public entrypoint for running a local pipeline.

    Args:
        pipeline_spec: PipelineSpec of the pipeline to run.
        arguments: User-provided arguments.

    Returns:
        The pipeline outputs.
    """

    # validate and access all global state in this function
    config.LocalExecutionConfig.validate()
    return _run_local_pipeline_implementation(
        pipeline_spec=pipeline_spec,
        arguments=arguments,
        raise_on_error=config.LocalExecutionConfig.instance.raise_on_error,
        pipeline_root=config.LocalExecutionConfig.instance.pipeline_root,
        runner=config.LocalExecutionConfig.instance.runner,
    )


def _run_local_pipeline_implementation(
    pipeline_spec: pipeline_spec_pb2.PipelineSpec,
    arguments: Dict[str, Any],
    raise_on_error: bool,
    pipeline_root: str,
    runner: config.LocalRunnerType,
) -> Dict[str, Any]:
    """Implementation of run local pipeline.

    Args:
        pipeline_spec: PipelineSpec of the pipeline to run.
        arguments: User-provided arguments.
        raise_on_error: Whether to raise an exception if a task exits with failure.
        pipeline_root: The local pipeline root.
        runner: The user-specified local runner.

    Returns:
        The pipeline outputs.
    """
    pipeline_name = pipeline_spec.pipeline_info.name
    # create pipeline resource name for the root pipeline
    from kfp.local import executor_input_utils
    pipeline_resource_name = executor_input_utils.get_local_pipeline_resource_name(
        pipeline_name)
    pipeline_name_with_color = logging_utils.format_pipeline_name(
        pipeline_spec.pipeline_info.name)

    with logging_utils.local_logger_context():
        logging.info(f'Running pipeline: {pipeline_name_with_color}')
        logging_utils.print_horizontal_line()

    executors = pipeline_spec.deployment_spec['executors']
    executors = {
        name: utils.struct_to_executor_spec(executor)
        for name, executor in executors.items()
    }

    # convert to dict for consistency with executors data structure in run_dag
    components = dict(pipeline_spec.components.items())
    io_store = io.IOStore()
    outputs, dag_status, fail_task_name = dag_orchestrator.run_dag(
        pipeline_resource_name=pipeline_resource_name,
        dag_component_spec=pipeline_spec.root,
        executors=executors,
        components=components,
        dag_arguments=arguments,
        io_store=io_store,
        pipeline_root=pipeline_root,
        runner=runner,
        unique_pipeline_id=placeholder_utils.make_random_id(),
    )
    if dag_status == status.Status.SUCCESS:
        status_with_color = logging_utils.format_status(status.Status.SUCCESS)
        with logging_utils.local_logger_context():
            logging.info(
                f'Pipeline {pipeline_name_with_color} finished with status {status_with_color}'
            )
        return outputs
    elif dag_status == status.Status.FAILURE:
        log_and_maybe_raise_for_failure(
            pipeline_name=pipeline_name,
            fail_task_name=fail_task_name,
            raise_on_error=raise_on_error,
        )
        return {}
    else:
        raise ValueError(f'Got unknown task status {dag_status.name}')


def log_and_maybe_raise_for_failure(
    pipeline_name: str,
    raise_on_error: bool,
    fail_task_name: Optional[str] = None,
) -> None:
    """To be called if an inner pipeline task exits with failure status. Either
    logs error or throws exception, depending on raise_on_error.

    Args:
        pipeline_name: The name of the root pipeline.
        raise_on_error: Whether to raise on error.
        fail_task_name: The name of the task that failed. None if no failure.
    """
    status_with_color = logging_utils.format_status(status.Status.FAILURE)
    pipeline_name_with_color = logging_utils.format_pipeline_name(pipeline_name)
    task_name_with_color = logging_utils.format_task_name(fail_task_name)
    msg = f'Pipeline {pipeline_name_with_color} finished with status {status_with_color}. Inner task failed: {task_name_with_color}.'
    if raise_on_error:
        raise RuntimeError(msg)
    with logging_utils.local_logger_context():
        logging.error(msg)
