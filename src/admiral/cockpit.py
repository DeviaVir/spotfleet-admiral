from admiral.aws import ClientCache
from admiral.model import RequestConfig
from botocore.exceptions import ClientError

import logging


logger = logging.getLogger('admiral')
request = RequestConfig()


def deploy(**args):  #pragma: no cover
    clients = ClientCache(args.get('region', 'us-east-1'))
    ec2 = clients.ec2()
    config = request.generate(args)

    if args.get('return_config'):
        return config

    if config:
        try:
            res = ec2.request_spot_fleet(config)
            return res.get('SpotFleetRequestId')
        except ClientError as e:
            logger.error('Spot Fleet Request failed, %s', e.message)
    else:
        logger.error('Invalid config found! Please check the parameters.')
