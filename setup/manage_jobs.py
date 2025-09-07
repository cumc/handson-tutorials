#!/usr/bin/env python3
import argparse
import csv
import subprocess
import re
import sys
import logging
import time
import os  

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
    auto_suspension_interval = args.auto_suspension_interval
    entrypoint_script = args.entrypoint_script_url

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
                    f"yes | float submit -a {opcenter} "
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
                    f"--dataVolume [mode=r,endpoint=s3.us-east-1.amazonaws.com]s3://rockefeller-course/AGIS/:/home/ubuntu/raw_data/ "
                    f"--dataVolume [mode=rw,endpoint=s3.us-east-1.amazonaws.com]s3://rockefeller-course/advstatgen_2025/{name_for_path}/:/home/ubuntu/handson-tutorials/ "
                    f"--env MODE=oem_packages "
                    f"--env GRANT_SUDO=yes "
                    f"--env VMUI=jupyter "
                    f"--env EFS={efs} "
                    f"--env PYDEVD_DISABLE_FILE_VALIDATION=1 "
                    f"--env JUPYTER_RUNTIME_DIR=/tmp/jupyter_runtime "
                    f"--env JUPYTER_ENABLE_LAB=TRUE "
                    f"--env ALLOWABLE_IDLE_TIME_SECONDS={auto_suspension_interval} "
                    f"--imageVolSize 3 "
                    f"--migratePolicy [disable=true,evadeOOM=false] "
                    f"--gateway {gateway} "
                    f"--publish 8888:8888"
                )
                
                # Add entrypoint script if specified
                if entrypoint_script:
                    command += f" --env ENTRYPOINT={entrypoint_script} "

                # Use subprocess.getoutput to get the full output (stdout + stderr)
                full_output = subprocess.getoutput(command)
                
                # Extract job ID from the output
                job_id = None
                
                # Look for 'id:' pattern first
                id_match = re.search(r'id:\s*(\S+)', full_output)
                if id_match:
                    job_id = id_match.group(1)
                else:
                    # Fallback: look for the last line that looks like a job ID
                    lines = full_output.strip().split('\n')
                    for line in reversed(lines):
                        line = line.strip()
                        # Job IDs are typically alphanumeric strings longer than 15 characters
                        if (line and 
                            not line.startswith('Warning') and 
                            not line.startswith('Login') and
                            not 'region' in line.lower() and
                            len(line) > 15 and 
                            re.match(r'^[a-zA-Z0-9]+$', line)):
                            job_id = line
                            break
                
                if job_id:
                    writer.writerow([name, job_id])
                    logging.info(f"Submitted job for {name} with Job ID: {job_id}")
                else:
                    logging.error(f"Failed to extract job ID for {name}")
                    logging.error(f"Full output: {full_output}")
                    
    except Exception as e:
        logging.error(f"Error in submit function: {e}")
        sys.exit(1)

def get_url(args):
    input_file = args.input
    output_file = args.output
    base_url = args.base_url
    output_address = []
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
                output_address.append([name, os.path.join(base_url, name.lower().replace(' ', '_'))])
                logging.info(f"Retrieved URL for {name}: {new_url}")
    except Exception as e:
        logging.error(f"Error in get_url function: {e}")
        sys.exit(1)
    # save output_address to a separate xlsx file
    try:
        import pandas as pd
        df = pd.DataFrame(output_address, columns=['Name', 'URL'])
        # remove the current extension and add .xlsx as the new extension
        df.to_excel(os.path.splitext(output_file)[0] + '.xlsx', index=False)
        logging.info("Saved interactive session job links to .xlsx")
    except ImportError:
        logging.warning("pandas not installed, skipping saving to xlsx file.")

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
    parser_submit.add_argument('--entrypoint_script_url', type=str, default=None, 
                               help="Optional entrypoint script URL to set as ENTRYPOINT environment variable.")
    parser_submit.add_argument('--efs', type=str, required=True, help="EFS configuration string.")
    parser_submit.add_argument('--auto_suspension_interval', type=int, default=25200, 
                               help="Auto suspension interval in seconds (default: 25200 = 7 hours).")
    parser_submit.set_defaults(func=submit)

    # Get URL command
    parser_get_url = subparsers.add_parser('get_url', help="Retrieve URLs for submitted jobs.")
    parser_get_url.add_argument('input', type=str, help="Input CSV file from the submit command.")
    parser_get_url.add_argument('output', type=str, help="Output CSV file with names, URLs, and job IDs.")
    parser_get_url.add_argument('--base_url', type=str, default='https://statgenetics.github.io/statgen-courses/', help="Base URL for interactive session job links.")
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