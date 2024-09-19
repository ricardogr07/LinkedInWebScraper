from setuptools import setup, find_packages

setup(
    name='LinkedInWebscraper',
    version='1.0.1',
    author="Ricardo García Ramírez",
    author_email="rgr.5882@gmail.com",
    description="A library for scraping LinkedIn job postings.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ricardogr07/LinkedInWebScraper",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.3',
        'pandas>=2.2.0',
        'numpy>=1.26.4',
        'openai>=1.43.0',
        'python-dotenv>=1.0.1'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
