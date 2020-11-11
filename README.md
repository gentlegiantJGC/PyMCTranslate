# PyMCTranslate

![Build](../../workflows/Build/badge.svg)
![Unittests](../../workflows/Unittests/badge.svg?event=push)
![Stylecheck](../../workflows/Stylecheck/badge.svg?event=push)
[![Documentation](https://readthedocs.org/projects/pymctranslate/badge)](https://pymctranslate.readthedocs.io)

PyMCTranslate is a translation system for Minecraft blocks, block entities, entities and items.
It enables translating data between a large number of Minecraft versions and platforms via an in-between format known as the Universal format.
This Universal format is a custom format independent of any Minecraft version and is designed to handle all data from any supported Minecraft version.  

The project is made up of a large number of specification and mapping files that are independent of any programming language making it a very flexible system.
These files are read by a small wrapper program that does what the mapping file says to do. Currently only a wrapper for Python 3 exists but others could be written.

# Amulet

This project was created for and is used by [Amulet](https://github.com/Amulet-Team/Amulet-Map-Editor) as a way to load the data from any world format into a consistent format.
This allows the editing of the data to be done in the same way regardless of what world format it has come from. This should solve a number of the issues that were present in MCEdit.
