import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ngeo", 
    version="0.0.1",
    author="Nigel Dsouza",
    author_email="",
    description="A small geo utility package for export and import",
    long_description="A small geo utility package that makes it easier to export and import shapefiles and feature classes to MySQL,Postgres",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
     install_requires=[
          'requests','tqdm'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)