# setup.py
from setuptools import setup, find_packages

setup(
    name='check-valid-hive-reward-json',
    use_scm_version={
        "local_scheme": "no-local-version",
    },
    author='stupidfish001',
    author_email='shovel@hscsec.cn',
    description='校验 .hive-reward.json 文件是否符合 HIVE-REWARD-DATASET 规范的工具',
    long_description=open('README.md',encoding='utf-8').read(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'check-topic = scripts.cli:run_tests',
        ]
    },
    install_requires=[
        'pytest',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)