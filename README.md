# Lambda python based over autoscaling lambda

To use this function, activate by triggering a CloudWatch event.
The function will check by pairs SQS queue that you want an autoscale group to scale up.

```
pairs = [{'queue_name': 'sqs_q1', 'autoscale_group': 'autoscale_group1'},
         {'queue_name': 'sqs_q2', 'autoscale_group': 'autoscale_group2'}]

```

When new SQS count >= Auto scale desired Count it will set a new desired count for the autoscale group

>It will consider the MaxSize of the auto scale group as the max size regardless the amount of messages in the queue

Make sure to have aws cli installed

```bash
brew update
brew install awscli
aws configure (enter your aws credentials)
```

To start using the project run
Install pip on your mac and virtualenv

```bash
sudo easy_install pip
sudo pip install virtualenv
```

Create virtual env in your project

```bash
virtualenv venv
```

Activate virtualenv folder that just was created

```bash
. ./venv/bin/activate
```

To build a packed lambda zip file run

```bash
make install
make build
```

To deploy the lambda zip file to AWS run

```bash
make deploy
```

To update github

```bash
make git_update
```

### Logging

Default logging is DEBUG.
To modify it, add to lambda LOG_LEVEL environment variable with the level needed.
