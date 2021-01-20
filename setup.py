from setuptools import setup, find_packages

setup(
    name='diavlos',
    version='0.1.0',
    packages=find_packages(include=['diavlos']),
    install_requires=[
        'pyyaml==5.3',
        'mwclient==0.10.1',
        'zeep==4.0.0',
        'Flask_HTTPAuth==4.1.0',
        'lxml==4.5.0',
        'Flask==1.1.1',
        'pymongo==3.11.0',
        'requests==2.22.0',
        'mwtemplates==0.4.0',
        'jsonschema==3.2.0',
        'aiohttp==3.7.3'
    ]
)
