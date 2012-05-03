from setuptools import setup, find_packages

setup(
        name='thug',
        version='0.2.9',
        author='',
        author_email='',
        scripts=['src/thug.py'],
        url='https://github.com/buffer/thug',
        package_dir = {'':'src'},
        package_data = {
            '': ['*.conf', '*.js'], 
        },
        packages=find_packages("src"),
        install_requires=[
            'PyV8',
            'html5lib',
            'beautifulsoup4',
            'httplib2>=0.7.4',
            'argparse',
            ],
        download_url='http://github.com/buffer/thug/tarball/master',
        license='COPYING',
        description='',
        long_description=open('README').read(),
        )
