#!/usr/bin/env python
import os
from eventify import Eventify

access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
region_name = os.getenv('REGION_NAME')
ev = Eventify(access_key, secret_key, 'TestStream', region_name=region_name)
