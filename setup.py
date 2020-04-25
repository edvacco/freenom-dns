import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="freenom", # Replace with your own username
    version="0.0.1",
    author="Nikolay Shamanovich",
    author_email="shm013@yandex.ru",
    description="Freenom DMS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shm013/freenom-dns",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
