import boto3
import logging
import os
import sys

logger = logging.getLogger(__name__)

if os.environ.get('LOG_LEVEL') is None:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.os.environ['LOG_LEVEL'])

if os.environ.get('AWS_REGION') is None:
    aws_region = 'us-east-1'
else:
    aws_region = os.environ.get('AWS_REGION')


pairs = [{'queue_name': 'sqs_q1', 'autoscale_group': 'autoscale_group1'},
         {'queue_name': 'sqs_q2', 'autoscale_group': 'autoscale_group2'}]

session = boto3.Session(region_name=aws_region)


def get_queue_and_count(sqs_name):
    client = session.client('sqs')
    response = client.list_queues(QueueNamePrefix=sqs_name)
    sqs_name = (response['QueueUrls'][0])
    attr = client.get_queue_attributes(QueueUrl=sqs_name,
                                       AttributeNames=['ApproximateNumberOfMessages'])
    sqs_count = (attr['Attributes']['ApproximateNumberOfMessages'])
    logger.info("Queue name is {0}, and count is {1}".format(sqs_name, sqs_count))
    return int(sqs_count)


def get_current_desired_capacity(autoscale_group_name):
    client = session.client('autoscaling')
    group = client.describe_auto_scaling_groups(AutoScalingGroupNames=[autoscale_group_name])
    autoscale_current_count = group['AutoScalingGroups'][0]['DesiredCapacity']
    autoscale_max_count = group['AutoScalingGroups'][0]['MaxSize']
    logger.info("Desired capacity from group {0} is {1}".format(autoscale_group_name, autoscale_current_count))
    return int(autoscale_current_count), int(autoscale_max_count)


def increase_desired_count_for_autoscaling_group(group_name, desired_count):
    client = session.client('autoscaling')
    try:
        client.set_desired_capacity(
            AutoScalingGroupName=group_name,
            DesiredCapacity=desired_count,
            HonorCooldown=True
        )
        logger.info("Auto scaling group {0} was set to {1} desired count".format(group_name, desired_count))
    except Exception as e:
        logger.fatal("The was a problem setting desired capacity of {0} for group {1}".format(desired_count, group_name))
        logger.fatal("{0}".format(e))
        raise


def lambda_handler(event, context):
    logger.info("Starting lambda...")
    for pair in pairs:
        sqs_count = get_queue_and_count(pair['queue_name'])
        autoscale_current_count, autoscale_max_capacity = get_current_desired_capacity(pair['autoscale_group'])
        logger.info("SQS Count for group {0} is {1} with instance desired count of {2}".format(pair['autoscale_group'], sqs_count, autoscale_current_count))

        if sqs_count >= autoscale_current_count:
            if sqs_count > autoscale_max_capacity:
                isntance_to_add = autoscale_max_capacity
            else:
                isntance_to_add = sqs_count + autoscale_current_count
            logger.info("I should set {0} desired count now".format(isntance_to_add))
            increase_desired_count_for_autoscaling_group(pair['autoscale_group'], isntance_to_add)


if __name__ == "__main__":
    event = ''
    context = []
    session = boto3.Session(profile_name='profile_name', region_name=aws_region)

    # Logger
    channel = logging.StreamHandler(sys.stdout)
    channel.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'))
    logger.addHandler(channel)

    lambda_handler(event, context)

