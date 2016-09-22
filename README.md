# spotfleet-admiral
SpotFleet Admiral

![89535d7f-48d2-4218-8ee4-3f0306dc3d7b](https://cloud.githubusercontent.com/assets/777823/18744748/87363288-80bf-11e6-9e48-0d43911fb266.jpg)

## Deploy

This library assumes your AWS credentials for Boto3 are already set up.

```
import admiral

specifications = {
	instance_types=['c3.large', 'c4.large'], // max 4
	subnets=['1-eeeeee'],
	user_data='your user data',
	iam_profile='arn:your-instance-profile',
	ami='ami-123123',
	security_groups='sg-123123',
	key_pair='key-name',
	ebs_optimized=False,
	block_devices=None, // you can pass an array of block devices
	placement=['us-east-1a', 'us-east-1b'], // not required if you are setting a subnet
	kernel=None, // pass a kernel ID
	monitoring=False, // enable instance monitoring
	network_interfaces=None, // pass an array of network interfaces
	ram=None, // pass a RamDiskId
	spot_price=None, // set a specific max for these instances (leave empty to use the SpotFleet max price)
	public_ip=True // associate a public IP for your instances
}

admiral.deploy(
	region='us-east-1', // spot region
	return_config=None, // return the config instead of trying to pass it on to AWS
	role='arn:this-spotfleet-role-is-required',
	strategy='diversified', // diversified || lowestPrice
	spot_price='2.000', // max price you ever want to pay for an instance
	specifications=specifications, // a separate object handled above
	capacity='2', // how many instances
	start_time=None, // when to bring up this spot fleet
	end_time=None // when to bring down this spot fleet
)
```

Review the tests for more implementation details.

