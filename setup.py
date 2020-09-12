import setuptools

setuptools.setup (
    name="scrapers",
    version="0.1",
    author="eteeeeeerminal",
    description="my scraping tools",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        "python-twitter==3.5",
        "beautifulsoup4==4.9.1"
    ],
    classifiers=[
        "programming Language :: Python :: 3.8"
        "Operating System :: OS Independent"
    ]
)