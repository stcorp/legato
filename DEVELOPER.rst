Developer Documentation
=======================

This document contains specific instructions for legato developers.

General
-------
The legato distribution consists of a single setuptools package.

The version numbering scheme for legato is ``x.y.z`` (``.z`` is optional):

- Increase the major version number ``x`` for changes that break backward
  compatibility.
- Increase the minor version number ``y`` for changes that add new features
  without breaking backward compatibility.
- Increase the revision number ``z`` for bug fixes.


Release procedure
-----------------
For the legato package:

- Update version number in ``setup.py``
- Update version number in ``README.rst``
- Update release date in ``README.rst``
- Check the list of dependencies in the ``README.rst``
- Check version numbers mentioned elsewhere in the ``README.rst``
- Check the upgrade instructions in ``README.rst``
- Add change history entry in ``CHANGES``
- Check copyright header (year range) in all files.
- Check that creation of the legatoe package using ``python setup.py sdist``
  runs without errors.

To create the legato package: ::

  $ python setup.py sdist

The package is now available in the ``dist`` directory.
