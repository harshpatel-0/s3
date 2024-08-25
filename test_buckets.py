"""
Module for unittests of the S3 backup functionality.
"""

import os
import unittest
from unittest.mock import patch
import datetime
import s3

class TestS3Backup(unittest.TestCase):
    """
    Class for unittests of the S3 backup functionality.
    """

    @patch('s3_backup.s3.list_buckets')
    def test_list_buckets(self, mock_list_buckets):
        """
        Test that the list_buckets function behaves as expected.
        """
        mock_list_buckets.return_value = {
            'Buckets': [{'Name': 'bucket1'}, {'Name': 'bucket2'}]
        }
        with patch('builtins.print') as mock_print:
            s3_backup.list_buckets()
            mock_print.assert_called_with('bucket2')
            self.assertEqual(mock_print.call_count, 2)

    @patch('s3_backup.s3.head_object')
    def test_get_s3_file_last_modified_found(self, mock_head_object):
        """
        Test get_s3_file_last_modified when file is found.
        """
        mock_head_object.return_value = {'LastModified': datetime.datetime(2024, 2, 13)}
        result = s3_backup.get_s3_file_last_modified('bucket', 'file')
        self.assertEqual(result, datetime.datetime(2024, 2, 13))

    @patch('s3_backup.s3.head_object')
    def test_get_s3_file_last_modified_not_found(self, mock_head_object):
        """
        Test get_s3_file_last_modified when file is not found.
        """
        mock_head_object.side_effect = s3_backup.ClientError(
            {'Error': {'Code': '404'}}, 'head_object')
        result = s3_backup.get_s3_file_last_modified('bucket', 'file')
        self.assertIsNone(result)
    @patch('s3_backup.s3.list_objects_v2')
    def test_list_contents(self, mock_list_objects_v2):
        """
        Test listing contents of a bucket.
        """
        mock_list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'server_folder/file1'},
                {'Key': 'server_folder/file2'}
            ]
        }
        with patch('builtins.print') as mock_print:
            s3_backup.list_contents('bucket', 'server_folder')
            mock_print.assert_any_call('server_folder/file1')
            mock_print.assert_any_call('server_folder/file2')
            self.assertEqual(mock_print.call_count, 2)

    @patch('s3_backup.s3.download_file')
    def test_download_object(self, mock_download_file):
        """
        Test downloading an object from a bucket.
        """
        s3_backup.download_object('bucket', 'server_folder', 'file1')
        expected_file_path = os.path.join('server_folder', 'file1')
        mock_download_file.assert_called_once_with(
            Bucket='bucket',
            Key=expected_file_path,
            Filename='file1'
        )

if __name__ == '__main__':
    unittest.main()
