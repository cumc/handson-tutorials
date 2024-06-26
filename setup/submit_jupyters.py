import argparse
import csv
import subprocess
import re

def submit(args):
    input_file = args.input
    output_file = args.output
    bucket_access_key = args.bucket_access_key
    bucket_secret_key = args.bucket_secret_key

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # writer.writerow(['Name', 'Job ID'])  # Write header

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

        # writer.writerow(['Name', 'URL', 'Job ID'])  # Write header

        # next(reader)  # Skip header row

        for row in reader:
            name, job_id = row
            ip_command = f"float show -j {job_id} | grep -A 1 portMappings | tail -n 1 | awk '{{print $4}}'"
            ip_address = subprocess.getoutput(ip_command).strip()

            log_command = f"float log -j {job_id} cat stderr.autosave | grep token= | head -n 1"
            url = subprocess.getoutput(log_command).strip()

            token = re.search(r'http://[^/]+/(lab\?token=[a-zA-Z0-9]+)', url).group(1)
            new_url = f"http://{ip_address}/{token}"

            writer.writerow([name, new_url, job_id])

def main():
    parser = argparse.ArgumentParser(description="Submit jobs and retrieve URLs using Float CLI.")
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

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

