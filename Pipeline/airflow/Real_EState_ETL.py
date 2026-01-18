from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from docker.types import Mount
from datetime import datetime 

default_args = {
    "owner": "Met",
    "depends_on_past": False,
    "retries": 1,
}

with DAG (dag_id="Real_EState_Pipeline",default_args=default_args,start_date=datetime(2026,1,1),schedule=None,catchup=False) as dag :
    scraping_bayut = DockerOperator(
                                 task_id="Scraping_Bayut_data",
                                 image="scraping:latest",
                                 api_version="auto",
                                 auto_remove="force",
                                 docker_url="unix://var/run/docker.sock", 
                                 network_mode="bridge",
                                 mount_tmp_dir=False,
                                mounts=[
                                  Mount(source="C:/bayut_data", target="/data", type="bind")
                                ]
                 )

    ssis_load_raw_data = SSHOperator(
        task_id="load_raw_data_by_ssis",
        ssh_conn_id="windows_ssis",
        command=r'"C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe" /F "Path\Load_raw_data.dtsx" /REPORTING E',
        cmd_timeout=None,
         )

    ssis_first_step_transformation = SSHOperator(
        task_id="first_step_transformation",
        ssh_conn_id="windows_ssis",
        command=r'"C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe" /F "Path\First_Step.dtsx" /REPORTING E',
        cmd_timeout=None,
        )

    ssis_second_step_transformation = SSHOperator(
        task_id="second_step_transformation",
        ssh_conn_id="windows_ssis",
        command=r'"C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe" /F "Path\Second_Step.dtsx" /REPORTING E',
        cmd_timeout=None,
        )
    
    ssis_last_step_transformation = SSHOperator(
        task_id="last_step_transformation",
        ssh_conn_id="windows_ssis",
        command=r'"C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe" /F "Path\Truncate_tables.dtsx" /REPORTING E',
        cmd_timeout=None,
        )
    
    
    scraping_bayut >> ssis_load_raw_data >> ssis_first_step_transformation >> ssis_second_step_transformation >> ssis_last_step_transformation

