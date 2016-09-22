from datetime import datetime, timedelta
from tzlocal import get_localzone
from pytz import utc
from mock import MagicMock, ANY
from admiral.model import RequestConfig

import unittest
import base64


class TestRequestConfig(unittest.TestCase):
    def setUp(self):
        self.request = RequestConfig()

    def test_generate(self):
        self.request._generate_specifications = MagicMock(return_value='test')

        result = self.request.generate({
            'role': 'test',
            'specifications': 'test'
        })

        config = result['SpotFleetRequestConfig']

        self.assertEqual(config['IamFleetRole'], 'test')
        self.assertEqual(config['SpotPrice'], '5.000')
        self.assertEqual(config['TargetCapacity'], '2')
        self.assertEqual(config['ExcessCapacityTerminationPolicy'], 'default')
        self.assertEqual(config['Type'], 'maintain')
        self.assertEqual(config['AllocationStrategy'], 'diversified')
        self.assertEqual(config['LaunchSpecifications'], 'test')
        self.assertTrue(config['ClientToken'])
        self.assertFalse('ValidFrom' in config)
        self.assertFalse('ValidUntil' in config)
        self.assertFalse('TerminateInstancesWithExpiration' in config)

        self.request._generate_specifications.assert_called_once_with('test')

    def test_generate_full(self):
        self.request._generate_specifications = MagicMock(return_value='test')
        now_utc = datetime.now(get_localzone()).astimezone(utc)
        start_time = now_utc + timedelta(days=14)
        end_time = start_time + timedelta(seconds=1)

        result = self.request.generate({
            'role': 'test',
            'strategy': 'test',
            'specifications': 'test',
            'spot_price': '1.000',
            'capacity': '4',
            'start_time': start_time,
            'end_time': end_time
        })

        config = result['SpotFleetRequestConfig']

        self.assertEqual(config['IamFleetRole'], 'test')
        self.assertEqual(config['SpotPrice'], '1.000')
        self.assertEqual(config['TargetCapacity'], '4')
        self.assertEqual(config['ExcessCapacityTerminationPolicy'], 'default')
        self.assertEqual(config['Type'], 'maintain')
        self.assertEqual(config['AllocationStrategy'], 'diversified')
        self.assertEqual(config['LaunchSpecifications'], 'test')
        self.assertEqual(config['ValidFrom'],
                         start_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.assertEqual(config['ValidUntil'],
                         end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.assertEqual(config['TerminateInstancesWithExpiration'],
                         True)
        self.assertTrue(config['ClientToken'])

        self.request._generate_specifications.assert_called_once_with('test')

    def test_generate_empty_launchspecifications(self):
        self.request._generate_specifications = MagicMock(return_value=None)
        result = self.request.generate({
            'role': 'test'
        })
        self.assertEqual(result, False)

    def test_generate_failed_launchspecifications(self):
        self.request._generate_specifications = MagicMock(return_value=None)
        result = self.request.generate({
            'role': 'test',
            'specifications': 'test'
        })
        self.assertEqual(result, False)

    def test_generate_empty_role(self):
        result = self.request.generate({})
        self.assertEqual(result, False)

    def test_generate_specifications(self):
        self.request._generator = MagicMock(return_value={'test': 'test'})
        result = self.request._generate_specifications({
            'instance_types': 'c4.large',
            'subnets': '1-eeeeee'
        })

        self.request._generator.assert_called_with('c4.large',
                                                   '1-eeeeee',
                                                   ANY)
        self.assertEqual(result[0]['test'], 'test')

    def test_generate_specifications_types(self):
        self.request._generator = MagicMock(return_value={'test': 'test'})
        result = self.request._generate_specifications({
            'instance_types': ['c4.large', 'c3.large'],
            'subnets': ['1-eeeeee', '1-bbbbbb']
        })
        self.request._generator.mock_calls[0].assert_called_with(
            'c4.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[1].assert_called_with(
            'c4.large',
            '1-bbbbbb',
            ANY)
        self.request._generator.mock_calls[2].assert_called_with(
            'c3.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[3].assert_called_with(
            'c3.large',
            '1-bbbbbb',
            ANY)
        self.assertEqual(result[0]['test'], 'test')
        self.assertEqual(result[1]['test'], 'test')
        self.assertEqual(result[2]['test'], 'test')
        self.assertEqual(result[3]['test'], 'test')

    def test_generate_specifications_types_too_many(self):
        self.request._generator = MagicMock(return_value={'test': 'test'})
        result = self.request._generate_specifications({
            'instance_types': ['c4.large', 'c3.large',
                               'm4.large', 'm3.large', 't2.medium'],
            'subnets': ['1-eeeeee', '1-bbbbbb']
        })
        self.request._generator.mock_calls[0].assert_called_with(
            'c4.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[1].assert_called_with(
            'c4.large',
            '1-bbbbbb',
            ANY)
        self.request._generator.mock_calls[2].assert_called_with(
            'c3.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[3].assert_called_with(
            'c3.large',
            '1-bbbbbb',
            ANY)
        self.request._generator.mock_calls[4].assert_called_with(
            'm4.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[5].assert_called_with(
            'm4.large',
            '1-bbbbbb',
            ANY)
        self.request._generator.mock_calls[6].assert_called_with(
            'm3.large',
            '1-eeeeee',
            ANY)
        self.request._generator.mock_calls[7].assert_called_with(
            'm3.large',
            '1-bbbbbb',
            ANY)
        self.assertEqual(result[0]['test'], 'test')
        self.assertEqual(result[1]['test'], 'test')
        self.assertEqual(result[2]['test'], 'test')
        self.assertEqual(result[3]['test'], 'test')
        self.assertEqual(result[4]['test'], 'test')
        self.assertEqual(result[5]['test'], 'test')
        self.assertEqual(result[6]['test'], 'test')
        self.assertEqual(result[7]['test'], 'test')
        self.assertEqual(len(result), 8)

    def test_generator(self):
        result = self.request._generator('c4.large', '1-eeeeee', {
            'user_data': 'testdata',
            'iam_profile': 'arn:test',
            'ami': 'testami',
            'security_groups': 'sg-test',
            'key_pair': 'test',
            'ebs_optimized': False,
            'block_devices': 'testdevices',
            'placement': 'us-east-1a',
            'kernel': 'testkernel',
            'monitoring': True,
            'network_interfaces': [{'testinterfaces': True}],
            'ram': 'testram',
            'spot_price': '1.000',
            'public_ip': True
        })

        self.assertEqual(result['NetworkInterfaces'][0]['SubnetId'],
                         '1-eeeeee')
        self.assertEqual(result['NetworkInterfaces'][0]['DeleteOnTermination'],
                         True)
        self.assertEqual(result['NetworkInterfaces'][0]['Groups'],
                         ['sg-test'])
        self.assertEqual(result['NetworkInterfaces'][0]
                               ['AssociatePublicIpAddress'],
                         True)
        self.assertEqual(result['BlockDeviceMappings'], 'testdevices')
        self.assertEqual(result['EbsOptimized'], False)
        self.assertEqual(result['IamInstanceProfile']['Arn'], 'arn:test')
        self.assertEqual(result['ImageId'], 'testami')
        self.assertEqual(result['InstanceType'], 'c4.large')
        self.assertEqual(result['KernelId'], 'testkernel')
        self.assertEqual(result['KeyName'], 'test')
        self.assertEqual(result['Monitoring']['Enabled'], True)
        self.assertEqual(result['NetworkInterfaces'][1]['testinterfaces'],
                         True)
        self.assertEqual(result['Placement']['AvailabilityZone'], 'us-east-1a')
        self.assertEqual(result['RamdiskId'], 'testram')
        self.assertEqual(result['SpotPrice'], '1.000')
        self.assertEqual(result['UserData'],
                         base64.b64encode('testdata').decode('utf-8').strip())

    def test_generator_multiple(self):
        result = self.request._generator('c4.large', '1-eeeeee', {
            'user_data': 'testdata',
            'iam_profile': 'arn:test',
            'ami': 'testami',
            'security_groups': ['sg-test1', 'sg-test2'],
            'key_pair': 'test',
            'ebs_optimized': False,
            'block_devices': 'testdevices',
            'placement': ['us-east-1a', 'us-east-1b'],
            'kernel': 'testkernel',
            'monitoring': True,
            'network_interfaces': [{'testinterfaces': True}],
            'ram': 'testram',
            'spot_price': '1.000',
            'public_ip': False
        })

        self.assertEqual(result['NetworkInterfaces'][0]['SubnetId'],
                         '1-eeeeee')
        self.assertEqual(result['NetworkInterfaces'][0]['DeleteOnTermination'],
                         True)
        self.assertEqual(result['NetworkInterfaces'][0]['Groups'],
                         ['sg-test1', 'sg-test2'])
        self.assertEqual(result['NetworkInterfaces'][0]
                               ['AssociatePublicIpAddress'],
                         False)
        self.assertEqual(result['BlockDeviceMappings'], 'testdevices')
        self.assertEqual(result['EbsOptimized'], False)
        self.assertEqual(result['IamInstanceProfile']['Arn'], 'arn:test')
        self.assertEqual(result['ImageId'], 'testami')
        self.assertEqual(result['InstanceType'], 'c4.large')
        self.assertEqual(result['KernelId'], 'testkernel')
        self.assertEqual(result['KeyName'], 'test')
        self.assertEqual(result['Monitoring']['Enabled'], True)
        self.assertEqual(result['NetworkInterfaces'][1]['testinterfaces'],
                         True)
        self.assertEqual(result['Placement']['AvailabilityZone'],
                         'us-east-1a,us-east-1b')
        self.assertEqual(result['RamdiskId'], 'testram')
        self.assertEqual(result['SpotPrice'], '1.000')
        self.assertEqual(result['UserData'],
                         base64.b64encode('testdata').decode('utf-8').strip())
