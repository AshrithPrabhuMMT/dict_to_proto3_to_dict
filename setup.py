from setuptools import setup

setup(
    name='dict_to_proto3_to_dict',
    version='0.1.2',
    author='Neeraj Koul',
    author_email='neeraj.koul@goibibo.com',
    description='A python helper library to create a proto3 object from a '
                'dict and also the other way round, i.e, a dict from a proto3 object. '
                'Handles Maps and filling up of default values in the dict created.',
    long_description=open("README.md").read(),
    url='https://github.com/goibibo/dict_to_proto3_to_dict',
    license='Public Domain',
    py_modules=['dict_to_proto3_to_dict'],
    packages=['dict_to_proto3_to_dict'],
    package_dir={'dict_to_proto3_to_dict': 'src'},
    install_requires=['protobuf>=3.0.0'],
    setup_requires=['protobuf>=3.0.0', 'nose>=1.0'],
    test_suite = 'nose.collector',
    classifiers=[
          'Programming Language :: Python',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ],
    keywords=['protobuf3',
              'protobuf',
              'dict to protobuf3',
              'protobuf3 to dict'
              'default dict'
              ]
)
