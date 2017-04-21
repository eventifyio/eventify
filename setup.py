from distutils.core import setup
from setuptools import find_packages

setup(
    name='eventify',
    packages=find_packages(),
    version='0.1.9',
    description='Event Driven Asynchronous Framework',
    author='Matthew Harris',
    author_email='matt@x-qa.com',
    url='https://github.com/morissette/eventify',
    download_url='https://github.com/morissette/eventify/dist/eventify-0.1.9.tar.gz',
    keywords=['event', 'event-driven', 'async',
              'framework', 'producer', 'consumer'],
    classifiers=[],
    install_requires=[
        'twisted',
        'pyOpenSSL',
        'autobahn',
        'service_identity'
    ]
)
