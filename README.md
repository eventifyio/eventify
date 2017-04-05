[![Build Status](https://travis-ci.org/morissette/eventify.svg?branch=master)](https://travis-ci.org/morissette/eventify)
<a href='https://coveralls.io/github/morissette/eventify?branch=master'><img src='https://coveralls.io/repos/github/morissette/eventify/badge.svg?branch=master' alt='Coverage Status' /></a>

# Eventify
A lightweight python module for building event driven distributed systems.

## Support
Currently only supports AWS Kinesis

## Sample Producer
```python
from eventify import Eventify

if __name__ == '__main__':
    client = Eventify(os.getenv('ACCESS_KEY'), os.getenv('SECRET_KEY'), 'TestStream', iterator_type='AT_SEQUENCE_NUMBER')
    client.create_topic()
    client.send_message("hello world")
```

## Sample Consumer
```python
from eventify import Eventify

if __name__ == '__main__':
    client = Eventify(os.getenv('ACCESS_KEY'), os.getenv('SECRET_KEY'), 'TestStream', iterator_type='AT_SEQUENCE_NUMBER')
    client.create_topic()
     
    while(True):
        commands = client.get_commands()
        for command in commands:
            handle_command(command)
```
