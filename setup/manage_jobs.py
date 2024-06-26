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
    bucket_access_key = args.bucket_access_key
    bucket_secret_key = args.bucket_secret_key
    gateway = args.gateway
    security_group = args.security_group
    image = args.image

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                name = row[1]
                pinyin = row[1].replace(' ', '_')
                job_name = pinyin
                command = (
                    f"yes | float submit -i docker.io/{image} -n {job_name} "
                    f"-e BUCKET_ACCESS_KEY={bucket_access_key} "
                    f"-e BUCKET_SECRET_KEY={bucket_secret_key} "
                    "--instType r5.large --publish 8888:8888 --vmPolicy '[onDemand=true]' "
                    "--migratePolicy '[disable=true]' "
                    f"--securityGroup {security_group} --withRoot=true --imageVolSize 50 --gateway {gateway} | grep 'id:' | awk -F'id: ' '{{print $2}}' | awk '{{print $1}}'"
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
    parser_submit.add_argument('--bucket_access_key', type=str, required=True, help="Bucket access key.")
    parser_submit.add_argument('--bucket_secret_key', type=str, required=True, help="Bucket secret key.")
    parser_submit.add_argument('--gateway', type=str, default='g-9xahbrb5rkbs0ic8yzylk', help="Gateway ID.")
    parser_submit.add_argument('--security_group', type=str, default='sg-02867677e76635b25', help="Security group ID.")
    parser_submit.add_argument('--image', type=str, default='yiweizh/rockefeller-jupyter', help="Docker image name.")
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

