"""
This module provides a CLI for backing up files to AWS S3, listing buckets, and other S3 operations.
"""

import os
import boto3
from botocore.exceptions import ClientError

# Initialize the S3 client
s3 = boto3.client('s3')

def main_menu():
    """Provide a command line interface for S3 operations."""
    while True:
        print("\nMain Menu:")
        print("1. List all buckets")
        print("2. Backup files to S3")
        print("3. List bucket objects")
        print("4. Download an object")
        print("5. Generate a pre-signed URL")
        print("6. List version information for an object")
        print("7. Delete an object from a bucket")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            list_buckets()
        elif choice == '2':
            local_folder = input("Enter the path of the local folder: ")
            bucket_name = input("Enter the S3 bucket name: ")
            backup_files(local_folder, bucket_name)
        elif choice == '3':
            bucket_name = input("Enter the S3 bucket name: ")
            server_folder_name = input("Enter the server folder name: ")
            list_contents(bucket_name, server_folder_name)
        elif choice == '4':
            bucket_name = input("Enter the S3 bucket name: ")
            server_folder_name = input("Enter the server folder name: ")
            file_name = input("Enter the object name: ")
            download_object(bucket_name, server_folder_name, file_name)
        elif choice == '5':
            bucket_name = input("Enter the S3 bucket name: ")
            object_name = input("Enter the object name: ")
            url = generate_presigned_url(bucket_name, object_name)
            print(f"Pre-signed URL: {url}")
        elif choice == '6':
            bucket_name = input("Enter the S3 bucket name: ")
            object_name = input("Enter the object name: ")
            list_object_versions(bucket_name, object_name)
        elif choice == '7':
            bucket_name = input("Enter the S3 bucket name: ")
            object_name = input("Enter the object name to delete: ")
            delete_object(bucket_name, object_name)
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again!")

def list_buckets():
    """List all buckets in the S3 account."""
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(bucket['Name'])

def get_s3_file_last_modified(bucket_name, file_name):
    """Get the last modified timestamp of a file in an S3 bucket."""
    try:
        response = s3.head_object(Bucket=bucket_name, Key=file_name)
        return response['LastModified']
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return None
        raise e

def backup_files(local_folder, bucket_name):
    """Backup files from a local folder to the specified S3 bucket."""
    for file_name in os.listdir(local_folder):
        file_path = os.path.join(local_folder, file_name)
        if os.path.isfile(file_path):
            s3_last_modified = get_s3_file_last_modified(bucket_name, file_name)
            local_last_modified = os.path.getmtime(file_path)

            if not s3_last_modified or local_last_modified > s3_last_modified.timestamp():
                s3.upload_file(file_path, bucket_name, file_name)
                print(f"Uploaded {file_name} to {bucket_name}")
            else:
                print(f"No changes were made to {file_name}, not uploading.")

def list_contents(bucket_name, server_folder_name=''):
    """List the contents of the specified folder in an S3 bucket."""
    if server_folder_name and not server_folder_name.endswith('/'):
        server_folder_name += '/'

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=server_folder_name)
    for obj in response.get('Contents', []):
        print(obj['Key'])

def download_object(bucket_name, server_folder_name, file_name):
    """Download an object from an S3 bucket."""
    file_path = os.path.join(server_folder_name, file_name)
    s3.download_file(
        Bucket=bucket_name,
        Key=file_path,
        Filename=file_name
    )
    print(f"Downloaded {file_name} from {bucket_name}")

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a pre-signed URL for an S3 object."""
    try:
        response = s3.generate_presigned_url ('get_object',
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        return None
    return response

def list_object_versions(bucket_name, object_name):
    """List all versions of an S3 object."""
    try:
        response = s3.list_object_versions(Bucket=bucket_name)
        for version in response.get('Versions', []):
            if version['Key'] == object_name:
                print(f"Version: {version['VersionId']} - Last Modified: {version['LastModified']}")
    except ClientError as e:
        print(e)

def delete_object(bucket_name, object_name):
    """Delete an object from an S3 bucket."""
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"Deleted {object_name} from {bucket_name}")
    except ClientError as e:
        print(e)

if __name__ == "__main__":
    main_menu()
