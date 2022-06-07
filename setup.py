import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="api-offres-emploi", 
    version="0.0.2",
    author="Etienne Kintzler",
    author_email="etienne.kintzler@gmail.com",
    description="Python interface to 'API Offres d'emploi v2' (Pole Emploi job search API)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/etiennekintzler/api-offres-emploi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
