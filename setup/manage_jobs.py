import argparse
import csv
import subprocess
import re
import sys

def submit(args):
    input_file = args.input
    output_file = args.output
    bucket_access_key = args.bucket_access_key
    bucket_secret_key = args.bucket_secret_key

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            name = row[1]
            pinyin = row[1].replace(' ', '_')
            job_name = pinyin
            command = (
                f"yes | float submit -i docker.io/yiweizh/rockefeller-jupyter -n {job_name} "
                f"-e BUCKET_ACCESS_KEY={bucket_access_key} "
                f"-e BUCKET_SECRET_KEY={bucket_secret_key} "
                "--instType r5.large --publish 8888:8888 --vmPolicy '[onDemand=true]' "
                "--migratePolicy '[disable=true]' --securityGroup sg-02867677e76635b25 "
                "--withRoot=true --imageVolSize 50 --gateway g-9xahbrb5rkbs0ic8yzylk | grep 'id:' | awk -F'id: ' '{print $2}' | awk '{print $1}'"
            )

            job_id = subprocess.getoutput(command).strip()
            writer.writerow([name, job_id])

def get_url(args):
    input_file = args.input
    output_file = args.output

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

def manage(args):
    action = args.action
    csv_file = args.csv_file

    valid_actions = ["suspend", "resume", "cancel"]
    if action not in valid_actions:
        print("Invalid action. Allowed actions are: suspend, resume, and cancel.")
        sys.exit(1)

    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        print("File not found:", csv_file)
        sys.exit(1)

    jobidlist = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            jobid = row[-1]
            jobidlist.append(jobid)

    for jobid in jobidlist:
        subprocess.run(["float", action, "-j", jobid, "-f"])

def main():
    parser = argparse.ArgumentParser(description="Submit jobs, retrieve URLs, and manage jobs using Float CLI.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Submit command
    parser_submit = subparsers.add_parser('submit', help="Submit jobs and generate job IDs.")
    parser_submit.add_argument('input', type=str, help="Input CSV file with names (first and last name per line).")
    parser_submit.add_argument('output', type=str, help="Output CSV file with names and job IDs.")
    parser_submit.add_argument('--bucket_access_key', type=str, required=True, help="Bucket access key.")
    parser_submit.add_argument('--bucket_secret_key', type=str, required=True, help="Bucket secret key.")
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
