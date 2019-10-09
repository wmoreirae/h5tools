import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="h5tools",
    version="0.0.1",
    author="Edson Moreira",
    author_email="w.moreira@gmail.com",
    description="A collection of tools to work with hdf5 files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where='.'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['h5packer = h5tools.image_packer:main']
    },
    install_requires=['h5py>=2.0.*', 'numpy>=1.17.*', 'pillow>=5.0.*'],
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, <4',
)