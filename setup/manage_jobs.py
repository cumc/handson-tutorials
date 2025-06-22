#!/usr/bin/env python3
import argparse
import csv
import subprocess
import re
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def submit(args):
    input_file = args.input
    output_file = args.output
    gateway = args.gateway
    security_group = args.security_group
    opcenter = args.opcenter
    bind_script = args.bind_script
    init_script = args.init_script
    efs = args.efs

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                name = row[-1]
                job_name = row[-1].replace(' ', '_')
                # Create a lowercase version for the dataVolume path
                name_for_path = name.replace(' ', '_').lower()

                command = (
                    f"float submit -a {opcenter} "
                    f"-i ghcr.io/statfungen/tmate-minimal "
                    f"-c 2 -m 16 "
                    f"--vmPolicy [onDemand=true] "
                    f"--securityGroup {security_group} "
                    f"--withRoot "
                    f"--allowList [r5*,r6*,r7*,m*] "
                    f"-j {bind_script} "
                    f"--hostInit {init_script} "
                    f"--dirMap /mnt/efs:/mnt/efs "
                    f"-n {job_name} "
                    f"--dataVolume [mode=r,endpoint=s3.us-east-1.amazonaws.com]s3://statfungen/ftp_fgc_xqtl/resource/references/:/home/ubuntu/reference_data "
                    f"--dataVolume [mode=r,endpoint=s3.us-east-1.amazonaws.com]s3://statfungen/ftp_fgc_xqtl/xqtl_protocol_data/:/home/ubuntu/xqtl_protocol_data "
                    f"--dataVolume [mode=rw,endpoint=s3.us-east-1.amazonaws.com]s3://statfungen/ftp_fgc_xqtl/interactive_sessions/al4225/xqtl_protocol_project/{name_for_path}/:/home/ubuntu/xqtl_protocol_project "
                    f"--env MODE=mount_packages "
                    f"--env GRANT_SUDO=yes "
                    f"--env VMUI=jupyter "
                    f"--env EFS={efs} "
                    f"--env PYDEVD_DISABLE_FILE_VALIDATION=1 "
                    f"--env JUPYTER_RUNTIME_DIR=/tmp/jupyter_runtime "
                    f"--env JUPYTER_ENABLE_LAB=TRUE "
                    f"--env ALLOWABLE_IDLE_TIME_SECONDS=7200 "
                    f"--imageVolSize 3 "
                    f"--migratePolicy [disable=true,evadeOOM=false] "
                    f"--gateway {gateway} "
                    f"--publish 8888:8888 | grep 'id:' | awk -F'id: ' '{{print $2}}' | awk '{{print $1}}'"
                )

                job_id = subprocess.getoutput(command).strip()
                writer.writerow([name, job_id])
                logging.info(f"Submitted job for {name} with Job ID: {job_id}")
    except Exception as e:
        logging.error(f"Error in submit function: {e}")
        sys.exit(1)

def get_url(args):
    input_file = args.input
    output_file = args.output

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                name, job_id = row
                ip_command = f"float show -j {job_id} | grep -A 1 portMappings | tail -n 1 | awk '{{print $4}}'"
                ip_address = subprocess.getoutput(ip_command).strip()

                log_command = f"float log -j {job_id} cat stderr.autosave | grep token= | head -n 1"
                url = subprocess.getoutput(log_command).strip()

                token = re.search(r'http://[^/]+/(lab\?token=[a-zA-Z0-9]+)', url).group(1)
                new_url = f"http://{ip_address}/{token}"

                writer.writerow([name, new_url, job_id])
                logging.info(f"Retrieved URL for {name}: {new_url}")
            writer.writerow([]) # need an empty row at the end, for GitHub Action to easily consolidate multiple lists to generate gh-pages
    except Exception as e:
        logging.error(f"Error in get_url function: {e}")
        sys.exit(1)

def manage(args):
    action = args.action
    csv_file = args.csv_file

    valid_actions = ["suspend", "resume", "cancel"]
    if action not in valid_actions:
        logging.error(f"Invalid action: {action}. Allowed actions are: {', '.join(valid_actions)}")
        sys.exit(1)

    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            jobidlist = [row[-1] for row in reader]
    except FileNotFoundError:
        logging.error(f"File not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        sys.exit(1)

    for jobid in jobidlist:
        try:
            if action in ["suspend", "cancel"]:
                subprocess.run(["float", action, "-j", jobid, "-f"], check=True)
            else:
                subprocess.run(["float", action, "-j", jobid], check=True)
            logging.info(f"Performed {action} on job ID: {jobid}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to perform {action} on job ID: {jobid}. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Submit jobs, retrieve URLs, and manage jobs using Float CLI.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Submit command
    parser_submit = subparsers.add_parser('submit', help="Submit jobs and generate job IDs.")
    parser_submit.add_argument('input', type=str, help="Input CSV file with names (first and last name per line).")
    parser_submit.add_argument('output', type=str, help="Output CSV file with names and job IDs.")
    parser_submit.add_argument('--gateway', type=str, default='g-sidlpgb7oi9p48kxycpmn', help="Gateway ID.")
    parser_submit.add_argument('--security_group', type=str, default='sg-02867677e76635b25', help="Security group ID.")
    parser_submit.add_argument('--opcenter', type=str, required=True, help="OpCenter address (e.g., 44.222.241.133).")
    parser_submit.add_argument('--bind_script', type=str, required=True, help="Path to bind mount script.")
    parser_submit.add_argument('--init_script', type=str, required=True, help="Path to host init script.")
    parser_submit.add_argument('--efs', type=str, required=True, help="EFS configuration string.")
    parser_submit.set_defaults(func=submit)

    # Get URL command
    parser_get_url = subparsers.add_parser('get_url', help="Retrieve URLs for submitted jobs.")
    parser_get_url.add_argument('input', type=str, help="Input CSV file from the submit command.")
    parser_get_url.add_argument('output', type=str, help="Output CSV file with names, URLs, and job IDs.")
    parser_get_url.set_defaults(func=get_url)

    # Manage command
    parser_manage = subparsers.add_parser('manage', help="Manage jobs (suspend, resume, or cancel).")
    parser_manage.add_argument('action', type=str, choices=['suspend', 'resume', 'cancel'], help="Action to perform on jobs.")
    parser_manage.add_argument('csv_file', type=str, help="CSV file with job IDs.")
    parser_manage.set_defaults(func=manage)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
