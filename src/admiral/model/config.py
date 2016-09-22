import logging
import uuid
import base64

logger = logging.getLogger('admiral')


class RequestConfig(object):
    def generate(self, args):
        role = args.get('role')
        strategy = args.get('strategy')
        specifications = args.get('specifications')
        spot_price = args.get('spot_price', '5.000')
        capacity = args.get('capacity', '2')
        start_time = args.get('start_time')
        end_time = args.get('end_time')

        print role
        if role is None or specifications is None:
            return False

        if strategy not in ['diversified', 'lowestPrice']:
            strategy = 'diversified'

        request = {
            'SpotPrice': spot_price,
            'ClientToken': str(uuid.uuid4()),
            'TargetCapacity': capacity,
            'ExcessCapacityTerminationPolicy': 'default',
            'AllocationStrategy': strategy,
            'IamFleetRole': role,
            'LaunchSpecifications': specifications,
            'Type': 'maintain'
        }

        if specifications:
            ls = self._generate_specifications(
                specifications)
            print ls
            if not ls:
                return False
            request['LaunchSpecifications'] = ls

        if start_time:
            request['ValidFrom'] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        if end_time:
            request['ValidUntil'] = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            request['TerminateInstancesWithExpiration'] = True

        request = {
            'SpotFleetRequestConfig': request
        }

        return request

    def _generate_specifications(self, specifications):
        instance_types = specifications.get('instance_types')
        subnets = specifications.get('subnets')

        collection = []

        if instance_types is None or subnets is None:
            return collection

        if not isinstance(instance_types, basestring):
            for instance_type in instance_types[0:4]:

                if not isinstance(subnets, basestring):
                    for subnet in subnets:
                        spec = self._generator(instance_type,
                                               subnet,
                                               specifications)
                        collection.append(spec)
                else:
                    spec = self._generator(instance_type,
                                           subnets,
                                           specifications)
                    collection.append(spec)
        else:
            if not isinstance(subnets, basestring):
                for subnet in subnets:
                    spec = self._generator(instance_types,
                                           subnet,
                                           specifications)
                    collection.append(spec)
            else:
                spec = self._generator(instance_types,
                                       subnets,
                                       specifications)
                collection.append(spec)

        return collection

    def _generator(self, instance_type, subnet, specifications):
        user_data = specifications.get('user_data')

        iam_profile = specifications.get('iam_profile')
        ami = specifications.get('ami')
        security_groups = specifications.get('security_groups')
        key_pair = specifications.get('key_pair')
        ebs_optimized = specifications.get('ebs_optimized', None)

        block_devices = specifications.get('block_devices')
        placement = specifications.get('placement')

        kernel = specifications.get('kernel')
        monitoring = specifications.get('monitoring', None)
        network_interfaces = specifications.get('network_interfaces')
        ram = specifications.get('ram')
        spot_price = specifications.get('spot_price')
        public_ip = specifications.get('public_ip', None)

        spec = {
            'NetworkInterfaces': [
                {
                  "SubnetId": subnet,
                  "DeleteOnTermination": True,
                  "AssociatePublicIpAddress": True
                }
            ]
        }

        if block_devices:
            spec['BlockDeviceMappings'] = block_devices
        if ebs_optimized is not None:
            spec['EbsOptimized'] = ebs_optimized
        if iam_profile:
            spec['IamInstanceProfile'] = {
                'Arn': iam_profile
            }
        if ami:
            spec['ImageId'] = ami
        if instance_type:
            spec['InstanceType'] = instance_type
        if kernel:
            spec['KernelId'] = kernel
        if key_pair:
            spec['KeyName'] = key_pair
        if monitoring is not None:
            spec['Monitoring'] = {
                'Enabled': monitoring
            }
        if network_interfaces:
            for interface in network_interfaces:
                spec['NetworkInterfaces'].append(interface)
        if security_groups:
            if isinstance(security_groups, basestring):
                security_groups = [security_groups]
            spec['NetworkInterfaces'][0]['Groups'] = security_groups
        if public_ip is not None:
            spec['NetworkInterfaces'][0]['AssociatePublicIpAddress'] = \
                public_ip
        if placement:
            if not isinstance(placement, basestring):
                placement = ','.join(placement)
            spec['Placement'] = {
                'AvailabilityZone': placement
            }
        if ram:
            spec['RamdiskId'] = ram
        if spot_price:
            spec['SpotPrice'] = spot_price
        if user_data:
            spec['UserData'] = \
                base64.b64encode(user_data).decode('utf-8').strip()

        return spec
