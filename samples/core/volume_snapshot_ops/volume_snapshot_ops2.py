# Copyright 2019 The Kubeflow Authors
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

import kfp
import kfp.dsl as dsl


@dsl.pipeline(name='volume')
def volume_pipeline():
    # create PersistentVolumeClaim (PVC)
    create_volume_task = dsl.VolumeOp(name='create_volume',
                                      resource_name='vol1',
                                      generate_unique_name=True,
                                      size='1Gi',
                                      modes=dsl.VOLUME_MODE_RWM)
    create_volume_task = dsl.VolumeOp(name='create_volume2',
                                      resource_name='vol1',
                                      generate_unique_name=True,
                                      size='1Gi',
                                      modes=dsl.VOLUME_MODE_RWM)

    # use PVC; write to file
    task_a = dsl.ContainerOp(name='step1_ingest',
                             image='alpine',
                             command=['sh', '-c'],
                             arguments=[
                                 'mkdir /data/step1 && '
                                 'echo hello > /data/step1/file1.txt'
                             ],
                             pvolumes={'/data': create_volume_task.volume})

    # use the same PVC again; read file
    task_b = dsl.ContainerOp(name='step2_gunzip',
                             image='library/bash:4.4.23',
                             command=['sh', '-c'],
                             arguments=['cat /data/step1/file.txt'],
                             pvolumes={'/data': create_volume_task.volume})

    # step1_snap = dsl.VolumeSnapshotOp(
    #     name="step1_snap",
    #     resource_name="step1_snap",
    #     volume=step1.pvolume
    # )

    # step2 = dsl.ContainerOp(
    #     name="step2_gunzip",
    #     image="library/bash:4.4.23",
    #     command=["sh", "-c"],
    #     arguments=["mkdir /data/step2 && "
    #                "gunzip /data/step1/file1.gz -c >/data/step2/file1"],
    #     pvolumes={"/data": step1.pvolume}
    # )

    # step2_snap = dsl.VolumeSnapshotOp(
    #     name="step2_snap",
    #     resource_name="step2_snap",
    #     volume=step2.pvolume
    # )

    # step3 = dsl.ContainerOp(
    #     name="step3_copy",
    #     image="library/bash:4.4.23",
    #     command=["sh", "-c"],
    #     arguments=["mkdir /data/step3 && "
    #                "cp -av /data/step2/file1 /data/step3/file3"],
    #     pvolumes={"/data": step2.pvolume}
    # )

    # step3_snap = dsl.VolumeSnapshotOp(
    #     name="step3_snap",
    #     resource_name="step3_snap",
    #     volume=step3.pvolume
    # )

    # step4 = dsl.ContainerOp(
    #     name="step4_output",
    #     image="library/bash:4.4.23",
    #     command=["cat", "/data/step2/file1", "/data/step3/file3"],
    #     pvolumes={"/data": step3.pvolume}
    # )


if __name__ == '__main__':
    ir_file = __file__.replace('.py', '.yaml')
    kfp.compiler.Compiler().compile(volume_pipeline, ir_file)

if __name__ == '__main__':
    import datetime
    import warnings
    import webbrowser

    from kfp import Client

    warnings.filterwarnings('ignore')
    # compiler.Compiler().compile(pipeline_func=my_pipeline, package_path=ir_file)
    pipeline_name = __file__.split('/')[-1].replace('_',
                                                    '-').replace('.py', '')
    display_name = datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S')
    job_id = f'{pipeline_name}-{display_name}'
    endpoint = 'https://75167a6cffcb723c-dot-us-central1.pipelines.googleusercontent.com'
    kfp_client = Client(host=endpoint)
    run = kfp_client.create_run_from_pipeline_package(ir_file, arguments={})
    url = f'{endpoint}/#/runs/details/{run.run_id}'
    print(url)
    webbrowser.open_new_tab(url)