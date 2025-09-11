#!/usr/bin/env python3
import csv
import subprocess
import sys
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_s3_folder(bucket_path):
    """使用 aws s3 命令创建 S3 文件夹"""
    try:
        # 创建一个空的 .keep 文件来确保目录存在
        command = [
            "aws", "s3", "cp", "-", f"s3://{bucket_path}/.keep",
            "--region", "us-east-1"
        ]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input="")
        
        if process.returncode == 0:
            logging.info(f"✓ Created directory: s3://{bucket_path}")
            return True
        else:
            logging.error(f"✗ Failed to create s3://{bucket_path}: {stderr}")
            return False
    except Exception as e:
        logging.error(f"✗ Error creating s3://{bucket_path}: {e}")
        return False



def create_student_directories(students_csv, base_path="srockefeller-course/advstatgen_2025"):
    """为学生列表中的每个学生创建个人目录"""
    
    success_count = 0
    failed_count = 0
    
    try:
        with open(students_csv, 'r') as infile:
            reader = csv.reader(infile)
            
            for row in reader:
                if not row or not row[-1].strip():  # Skip empty rows
                    continue
                    
                name = row[-1].strip()
                # Convert name to username format (lowercase, underscore)
                username = name.lower().replace(' ', '_')
                
                # Create the S3 path for this student
                student_path = f"{base_path}/{username}"
                
                logging.info(f"Creating directory for {name} (username: {username})")
                
                if create_s3_folder(student_path):
                    success_count += 1
                else:
                    failed_count += 1
                    
    except FileNotFoundError:
        logging.error(f"File not found: {students_csv}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    logging.info(f"\n=== Summary ===")
    logging.info(f"Successfully created: {success_count} directories")
    logging.info(f"Failed to create: {failed_count} directories")
    
    return success_count, failed_count

def list_existing_directories(base_path="rockefeller-course/advstatgen_2025"):
    """列出已存在的学生目录"""
    try:
        command = ["aws", "s3", "ls", f"s3://{base_path}/", "--region", "us-east-1"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            logging.info("Existing student directories:")
            for line in result.stdout.strip().split('\n'):
                if 'PRE' in line:  # PRE indicates a directory
                    dir_name = line.split()[-1].rstrip('/')
                    logging.info(f"  - {dir_name}")
        else:
            logging.info("No existing student directories found")
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list directories: {e}")
    except Exception as e:
        logging.error(f"Error listing directories: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Create student directories in S3 bucket")
    parser.add_argument('students_csv', help="CSV file with student names")
    parser.add_argument('--base-path', default="rockefeller-course/advstatgen_2025",
                       help="Base S3 path for student directories")
    parser.add_argument('--list-existing', action='store_true',
                       help="List existing directories")
    
    args = parser.parse_args()
    
    if args.list_existing:
        list_existing_directories(args.base_path)
        return
    
    logging.info(f"Creating student directories under: s3://{args.base_path}")
    
    # Check if AWS CLI is available
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("AWS CLI is not available. Please install and configure AWS CLI first.")
        logging.error("Installation: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html")
        logging.error("Configuration: aws configure")
        sys.exit(1)
    
    # Create directories
    success, failed = create_student_directories(args.students_csv, args.base_path)
    
    if failed > 0:
        logging.warning("Some directories failed to create. Please check AWS credentials and permissions.")
        sys.exit(1)
    else:
        logging.info("All student directories created successfully!")

if __name__ == '__main__':
    main()