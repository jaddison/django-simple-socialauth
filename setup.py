from __future__ import unicode_literals
from setuptools import setup, find_packages

import simple_socialauth

setup(
    name='django-simple-socialauth',
    version=simple_socialauth.__version__,
    description="Django social account authentication app based on requests-oauthlib.",
    long_description='View `django-simple-socialauth documentation on Github  <https://github.com/jaddison/django-simple-socialauth>`_.',
    keywords='django social authentication oauth register login auth',

    url='https://github.com/jaddison/django-simple-socialauth',

    author='jaddison',
    author_email='addi00+github.com@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['requests-oauthlib'],
)
