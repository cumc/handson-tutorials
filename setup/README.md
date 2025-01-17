# How to setup tutorial servers on MMCloud

For more detailed explanation of the setup, you can refer [to the documentation here](https://wanggroup.org/productivity_tips/mmcloud-interactive).

## Setup EFS for Package Installation (one-time setup)

As of 1/16/2025, packages will be installed onto an EFS for all users to use, rather than rely on large docker images per user with packages pre-installed. This setup will require a one-time step of installing said packages into the EFS first.

Assuming that 

- The gateway has been set up in the Opcenter.
- The security group for port 8888 is created in the AWS console.
- The EFS has been created
- The latest version of the `mm_jobman.sh` script is cloned. You can find it [here on GitHub](https://github.com/rfeng2023/mmcloud/tree/main/example).

Run the command below to start `shared-admin` mode, which will allow you to install packages as an admin for all other users to access as shared packages. Fill in the necessary parameters that are encapsulated in `<>`.

```bash
mm_jobman.sh -o <OPCENTER_IP> \
-ide tmate \
-g <GATEWAY_ID> \
-sg <SECURITY_GROUP> \
-efs <EFS_IP> \
--shared-admin \
-ivs 20
```

When prompted, input your account details: your OpCenter username and password. Then, a connection to the interactive session will be established from your shell terminal. You will see the below message. Just type `y` and enter to continue.

```
NOTICE: tmate sessions are primarily designed for initial package configuration.
For regular development work, we recommend utilizing a more advanced Integrated Development Environment (IDE)
via the -ide option, if you have previously set up an alternative IDE.
Do you wish to proceed with the tmate session? (y/N): y
```

A few minutes later, you should see the output:

```bash
To access the server, copy this URL into a browser: ...
```

or

```bash
SSH session: ...
```

Copy the URL into your web browser. For the SSH session, you may copy that into your terminal.

Upon accessing the tmate session, you may now install packages directly into the EFS. Please run the command below to get started on installing the initial packages.
``` bash
curl -fsSL https://raw.githubusercontent.com/gaow/misc/master/bash/pixi/pixi-setup.sh | bash
```

Then, install the course-specific courses with the commands below:
```bash
pixi global install --environment r-base $(curl -fsSL https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/r_packages.txt | grep -v "#" | tr '\n' ' ')
pixi global install --environment python $(curl -fsSL https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/python_packages.txt | grep -v "#" | tr '\n' ' ')
pixi clean cache -y
```

Overall, this should take an hour to install everything. Ideally, you would only need to do this once.

The purpose of this job is to setup packages. **Once you are done with the setup, you can quite the `tmate` session and cancel the job to stop the charges.**

## Start a Server using `mm_jobman.sh`

The user may now create a server to start accessing the shared packages that were just installed. With the same script, below is the command to submit the jupyter interactive job for the course. The end user will need to modify the `<>` variables according to their own environment.
```bash
mm_jobman.sh -o <OPCENTER_IP> \
 -g <GATEWAY_ID> \
 -sg <SECURITY_GROUP> \
 -efs <EFS_IP> \
 --oem-packages \
 -jn <job_name> \
 -ide jupyter \
 -u <username> \
 -p <password>
```
CLI Options Breakdown:
- `-g` Specify the gateway you want the job to be attached to
- `-sg` Specify the AWS security group to allow inbound access to port 8888
- `-efs` Specify the EFS IP, which houses the installed packages
- `--oem-packages` An interactive job mode that allows the user to use only shared packages
- `-jn` Job name
- `-ide` Specify the job's IDE. Can be access through the browser
- `-u` The user's OpCenter username (script will ask if not given)
- `-p` The user's Opcenter password (script will ask if not given)

## Retrieve Login Token for the server

### CLI Way
Remember to substitite your job ID.

The first step is to get the IP address and the port.
```
IP_ADDRESS=$(float show -j "$jobid" | grep -A 1 portMappings | tail -n 1 | awk '{print $4}')
```

The second step is to retrieve the login url from the log and strip out the token.
```
url=$(float log -j "$jobid" cat stderr.autosave | grep token= | head -n 1)
token=$(echo "$url" | sed -E 's|.*http://[^/]+/(lab\?token=[a-zA-Z0-9]+).*|\1|')
```

The actual url could be constructed as follow:
```
new_url="http://$IP_ADDRESS/$token"
```
### Manual Way  (for reference; don't do this)
After the job is in `Execution` stage on MMC, please retrieve the Jupyter login token in stderr.autosave.
Inside your job, go to Attachments -> stderr.autosave, and search for:
```
[I 2024-04-09 21:56:49.090 ServerApp] Jupyter Server 2.13.0 is running at:
[I 2024-04-09 21:56:49.090 ServerApp] http://9486a94be75a:8888/lab?token=e466d716b939274a422d23a4b0aac9a68d4b408f6c9da644
[I 2024-04-09 21:56:49.090 ServerApp]     http://127.0.0.1:8888/lab?token=e466d716b939274a422d23a4b0aac9a68d4b408f6c9da644
```
where you could substitute `127.0.0.1` with the IP of the host instance, and paste the link inside a web browser.

## Suspend, resume and cancel

```
float suspend -j <job_id>
float resume -j <job_id>
float cancel -j <job_id>
```

## For teaching assistants

### Goal

- For a list of student names (in English) generate generate a file [like this](https://github.com/statgenetics/statgen-courses/blob/master/.github/workflows/rockefeller_2024.csv) and send a PR to that folder. It can be any name but should have `csv` format and extension. **The last line of this file should be empty line**.
- A couple of minutes after the PR is accepted, test if for a student listed in the CSV file, the corresponding server is avaiable as `https://statgenetics.github.io/statgen-courses/<firstname_lastname>`

### Setting up servers

- To set up servers, you will need to use a script [like this](https://github.com/cumc/handson-tutorials/blob/main/setup/manage_jobs.py) to submit jobs to cloud at the same time.
- Also, a list of student names will need to be proveide, showing as following:
  ```
  Wang Chao
  Zheng Wei Gang
  ```
  This list only need one column as input. If in the case that you have Chinese vs English names for student, just make sure put the English names as the last column. This script will always load the last column of this list. 

- The script has three sections:
    - `submit`: this is to submit jobs and get job ID generated by `float` command
        - To submit jobs, please include all the information in the following command:
        ```
        python manage_jobs.py submit <input.csv> <output_from_submit.csv> --bucket_access_key <access_key> --bucket_secret_key <secret_key> --gateway <gateway> --security_group <group> --image <image>
        ```
        For example
        ```
        python manage_jobs.py submit names_agis.csv names_agis_submit.csv --bucket_access_key <access_key> --bucket_secret_key <secret_key> --gateway g-9xahbrb5rkbs0ic8yzylk --security_group sg-02867677e76635b25 --image yiweizh/rockefeller-jupyter
        ``` 
        - This step will generate a `csv` file that have two columns, Name and Job ID.
        ```
        Wang Chao,d6fioprtyruft80elx7mn
        Zheng Wei Gang,z0xo3ca8s50j5pnrh2wyi
        ```
       **At this point all jobs are submitted to MMCloud. You need to keep track of these jobs on the OpCenter to make sure they are all "Executing" before moving on to the next step.**
    - `get_url`: this step will collect all the URL generated for each job
        - The output from `submit` will be used to collect URL
        ```
        python manage_jobs.py get_url <output_from_submit.csv> <output_from_geturl.csv>
        ```
        For example,
        ```
        python manage_jobs.py get_url names_agis_submit.csv shenzhen_2024.csv
        ```
        - A list of student names, URL, and job ID will be generated [like this](https://github.com/statgenetics/statgen-courses/blob/master/.github/workflows/shenzhen_2024.csv).
        - After PR the list, the corresponding server is avaiable as `https://statgenetics.github.io/statgen-courses/<firstname_lastname>`
    - `manage`: To suspend, resume, or cancel jobs, `manage` section be can used to do so
        - The output file from `get_url` will be used to manage job status
        ```
        python manage_jobs.py manage <suspend/resume/cancel> <output_from_geturl.csv>
        ```
        For example,
        ```
        python manage_jobs.py manage <suspend/resume/cancel> shenzhen_2024.csv
        ```

### Maintenance when on low budget

For Maintenance,
- After everything is setup and tested, we should keep all the instances suspended
- Right before lab session, we resume all instances
- Right after the lab session ends, we suspend again
- If anyone has an issue with their server for whatever reason, we will need to start a new one for him/her (submit job and add a line to the CSV file), and cancel the old one that no longer works.
