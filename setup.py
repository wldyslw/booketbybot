from setuptools import (
    setup,
    find_packages
 )

setup(
    name='booketbybot',
    version='0.0.1',
    description='booket.by telegram bot for administrating purposes',
    author='Uladzislau Maltsau',
    author_email='wldyslw@outlook.com',
    url='https://github.com/wldyslw/booketbybot',
    install_requires=['sqlalchemy', 'requests', 'python-dotenv', 'python-telegram-bot']
)