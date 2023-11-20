# Copyright 2023 The Kubeflow Authors
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
"""Tests for pipeline_task_base.py."""
import unittest

from kfp.dsl import pipeline_task_base


class TestPipelineTaskBase(unittest.TestCase):

    def test_incomplete_concrete_class(self):

        class IncompletePipelineTask(pipeline_task_base.PipelineTaskBase):

            @property
            def outputs(self) -> str:
                return 'foo'

        with self.assertRaisesRegex(
                TypeError,
                r"Can't instantiate abstract class IncompletePipelineTask with abstract methods"
        ):
            IncompletePipelineTask()


if __name__ == '__main__':
    unittest.main()
