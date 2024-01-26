# Copyright 2022 The Kubeflow Authors
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

from typing import Dict, List

from kfp import compiler
from kfp import dsl
from kfp.dsl import component


@component
def print_text(msg: str):
    print(msg)


@component
def print_int(x: int):
    print(x)


@component
def list_dict_maker() -> List[Dict[str, int]]:
    return [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 4}]

@dsl.pipeline(name='pipeline-with-loops')
def my_pipeline(loop_parameter: List[str]):

    # Loop argument is from a pipeline input
    with dsl.ParallelFor(items=loop_parameter, parallelism=2) as item:
        print_text(msg=item)

        with dsl.ParallelFor(items=loop_parameter) as nested_item:
            print_text(msg=nested_item)

    # Loop argument is a static value known at compile time
    loop_args = [{'A_a': '1', 'B_b': '2'}, {'A_a': '10', 'B_b': '20'}]
    with dsl.ParallelFor(items=loop_args, parallelism=0) as item:
        print_text(msg=item.A_a)
        print_text(msg=item.B_b)

        nested_loop_args = [{
            'A_a': '10',
            'B_b': '20'
        }, {
            'A_a': '100',
            'B_b': '200'
        }]
        with dsl.ParallelFor(
                items=nested_loop_args, parallelism=1) as nested_item:
            print_text(msg=nested_item.A_a)
            print_text(msg=nested_item.B_b)

    # Loop argument that is a static dictionary known at compile time.
    dict_loop_argument = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 4}]
    with dsl.ParallelFor(items=dict_loop_argument, parallelism=1) as item:
        print_int(x=item.a)

    # Loop argument that coming from the upstream component.
    t = list_dict_maker()
    with dsl.ParallelFor(t.output) as item:
        print_int(x=item.a)


if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path=__file__.replace('.py', '.yaml'))
