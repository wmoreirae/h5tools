"""
HDF5 Image Packer

This little utility helps on packing images into matrices in an hdf5 file.
It works by collecting all the images from a folder, resizing them to match a
single size, and bundling them in a 3d matriz named after their folder of
origin.
It can handle packing images from multiple folders.
It doesn't work recursively. Each folder must be explicitly named.
"""

from pathlib import Path
import numpy as np
from PIL import Image
import h5py
import argparse
import logging


def _shape_(shape: str):
    return tuple((int(x) for x in shape.split('x')))


def _getOptions_() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create HDF5 files from folders of images")
    parser.add_argument('-v', '--verbose',
                        default=0,
                        action='count',
                        help='Verbose mode. -v for Info, -vv is for Debug')
    parser.add_argument('-r', '--root',
                        type=str,
                        default=r"/",
                        help="The name to be used as root for this data group")
    parser.add_argument('-s', '--shape',
                        type=_shape_,
                        default=None,
                        help="A shape like '640x480' or '120x120' "
                        + "for an image")
    parser.add_argument('source',
                        type=Path,
                        nargs='+',
                        help="A space-separated list of folders "
                        + "to be user as source with the caveat "
                        + "that the folder name will be used as "
                        + "the name for the dataset")
    parser.add_argument('-o', '--output',
                        type=str,
                        required=True,
                        help="The name of the output file")

    options = parser.parse_args()
    return options


def _verbosity_(v_level):
    """Sets the verbosity level"""
    v_level = 2 if v_level > 2 else v_level

    if 0 == v_level:
        logging.basicConfig(level=logging.WARNING)
    elif 1 == v_level:
        logging.basicConfig(level=logging.INFO)
    elif 2 <= v_level:
        logging.basicConfig(level=logging.DEBUG)

    logging.info("Set the verbosity level to {level}."
                 .format(level=['WARNING', 'INFO', 'DEBUG'][v_level]))


def _isImageFile_(path):
    extension = path.suffix.lower()
    return extension in ['.jpeg', '.jpg', '.png', '.bmp']


def _mapDatasetsToFiles_(sources):
    """Create a dict linking source names to image files inside said sources"""
    dses = dict()
    for src in sources:
        files = [file for file in src.iterdir() if src.is_dir()]
        if src.is_file():
            files.append(src)
        # filter non-image files
        files = [file for file in files if _isImageFile_(file)]
        if 0 == len(files):
            logging.warning("Source {src} has 0 files! Ignoring it..."
                            .format(src=src))
            continue
        logging.debug("Added {n} files from folder {src!s}: \n{files!r:20}"
                      .format(n=len(files), src=src, files=files))
        dses[src.name] = files
    if 0 == len(dses.keys()):
        logging.warning("Couldn't find a single dataset! Exitting...")
        exit(0)
    return dses


def _getShape_(dataset_files, key=None):
    """Gets the shape of the first file on a dataset or group of datasets.

       This gets used if a shape is not given by the user.
       It opens the file on a dataset map and get its shape
    """
    logging.debug("Trying to read shape from a file")
    keys = dataset_files.keys()
    if key is None:
        file = dataset_files[keys[0]][0]
    else:
        file = dataset_files[key][0]
    try:
        logging.debug("Trying to open file {file}"
                      .format(file=file.absolute()))
        with Image.open(file.absolute()) as image:
            logging.debug("Sucessfully opened file {file}"
                          .format(file=file.absolute()))
            return image.size
    except OSError:
        logging.error("Couldn't read image from file {file}! Exitting..."
                      .format(file=file.absolute()))
        exit(1)


def _saveToHDF5_(filename, dataset_files, shape, root):
    """Creates an hdf5 file and start filling it with data one item at a time
    """
    try:
        logging.info("Opening or creating an hdf5 file")
        with h5py.File(filename, mode='a') as hdf:
            logging.debug("Hdf5 file opened sucessfully")
            for name in dataset_files.keys():
                n_elements = len(dataset_files[name])

                # check for the shape
                if shape is None:
                    width, height = _getShape_(dataset_files, name)
                    d_shape = (n_elements, height, width)
                else:
                    d_shape = (n_elements, *shape)

                group = hdf.require_group(root)
                # Check if the name already exists in the root group
                if name in group.keys():
                    logging.warning(("Name {name} already exists in group "
                                     "{group}! Skipping...")
                                    .format(name=name, group=root))
                    continue

                # Create the dataset
                dataset = group.create_dataset(name=name,
                                               shape=d_shape,
                                               dtype='uint8')
                for i, path in enumerate(dataset_files[name]):
                    try:
                        logging.debug("Opening image file {}"
                                      .format(path.absolute()))
                        with Image.open(path.absolute()) as image:
                            logging.debug("Image file opened sucessfully")
                            data = image.convert(mode='L')
                            if data.size != (width, height):
                                data = data.resize((width, height,),
                                                   resample=Image.BICUBIC)
                            dataset[i] = np.array(data, dtype="uint8")
                    except IOError:
                        logging.error("Could not open file {name}! Skipping..."
                                      .format(name=path.absolute()))

    except OSError as err:
        logging.error("Error with output file: {error:s}\nExitting..."
                      .format(error=err.strerror))
        exit(1)


def main():
    options = _getOptions_()
    _verbosity_(options.verbose)
    logging.info('Started HDF5 packer')
    datasets_files = _mapDatasetsToFiles_(options.source)
    _saveToHDF5_(options.output, datasets_files, options.shape, options.root)


if __name__ == "__main__":
    main()
