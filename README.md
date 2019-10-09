# h5tools
A collection of utilities to work with HDF5 files

For now there is only a single tool h5packer which helps on packing images into matrices in an hdf5 file.
It works by collecting all the images from a folder, resizing them to match a single size, and bundling them in a 3d matrix named after their folder of
origin.
It can handle packing multiple folders into matrixes, but it doesn't work recursively. Each folder must be passed explicitly as a parameter.
