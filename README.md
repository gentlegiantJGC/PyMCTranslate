# PyMCTranslate
This project is a library of block mappings that can be used to convert from any Minecraft format into any other Minecraft format. (That is the plan anyway).

It does this by converting the local block definition into the Universal format which is a format separate to any version and then from that into the output format.

The Universal format is modeled on the Java 1.13+ format with modifications in places that make sense.

To implement these mappings into your project you will just need the contents of the [mappings](mappings) directory and a reader written in the language of the application. A example Python reader can be found [here](reader/data_version_handler.py).

# Contributing

Contributions to the project are accepted. Please read the more in-depth explanation about the project compiler [here](compiler).
