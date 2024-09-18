from setuptools import setup, find_packages

setup(
    name='LinkedInWebscraper',
    version='0.2.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
        'numpy',
        'openai', 
        'python-dotenv'
    ],
)
