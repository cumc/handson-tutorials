# How to submit a job to MMCloud (in the course setting)
## Login to the Opcenter
You would need to log in before submitting jobs to launch the Jupyter instances.
```
float login -u <username> -p <password> -a <opcenter_IP>
```

## Submit the job using Float CLI
The below is the command to submit the jupyter interactive job as the course, the end user will need to modify the `securityGroup` or `gateway` as his/she own environment.
```
float submit -i docker.io/yiweizh/rockefeller-jupyter -n Jupyter_Instance --instType r5.large --publish 8888:8888 --vmPolicy [onDemand=true] --migratePolicy [disable=true] --securityGroup sg-0fa5bd545c482d41a --withRoot=true --imageVolSize 30 --gateway g-30bgec3fbfeff8szxz28g
```
CLI Options Breakdown:
- `-i` Container image URL
- `-n` Job Name
- `--instType` The instance type you want to host the Jupyter server on
- `--publish` Port mapping between container and host
- `--vmPolicy [onDemand=true]` Specify the instance to be on-demand, so it won't have spot reclaims from AWS
- `--migratePolicy [disable=true]` Specify the migration policy to be disabled
- `--securityGroup` Specify the AWS security group to allow inbound access to port 8888
- `--imageVolSize` Specify the EBS volume size that backs up the file system for the container
- `--gateway` (Optional) Specify the gateway you want the job to be attached to


# Retrieve Login Token
After the job is in `Execution` stage on MMC, please retrieve the Jupyter login token in stderr.autosave.
Inside your job, go to Attachments -> stderr.autosave, and search for:
```
[I 2024-04-09 21:56:49.090 ServerApp] Jupyter Server 2.13.0 is running at:
[I 2024-04-09 21:56:49.090 ServerApp] http://9486a94be75a:8888/lab?token=e466d716b939274a422d23a4b0aac9a68d4b408f6c9da644
[I 2024-04-09 21:56:49.090 ServerApp]     http://127.0.0.1:8888/lab?token=e466d716b939274a422d23a4b0aac9a68d4b408f6c9da644
```
, where you could substitute `127.0.0.1` with the IP of the host instance, and paste the link inside a web browser.