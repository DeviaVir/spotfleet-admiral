import unittest

from mock import patch
from admiral.aws.clients import ClientCache

REGION = 'us-east-1'


class TestClientCache(unittest.TestCase):
    def setUp(self):
        self.clients = ClientCache(REGION)

    @patch('admiral.aws.clients.boto3')
    def test_ec2(self, mock_boto3):
        self.clients.ec2()
        mock_boto3.client.assert_called_once_with('ec2', REGION)

    @patch('admiral.aws.clients.boto3')
    def test_ec2_cached(self, mock_boto3):
        self.clients.ec2()
        self.clients.ec2()
        self.assertEqual(1, mock_boto3.client.call_count)
