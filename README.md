# Header-Compilation-Check
Small Python programm that checks if header files of c++ code compile without any implementation files

This is not a finished program!

This small python programm is intended for use in project tests and for personal usage.
There is a guideline in C++ and C that header files should compile on their own.
This program is meant to check this while providing a simple way to go over code that has grown over time.
When executed, the already passed, headers are saved in a txt file and in the next run are loaded so that
a recompilation of the already passed headers is not necessary and you can fix the headers one by one without
much waiting time.
With the silent flag the program has no output and returns a non zero value if compilations fails for one or more headers
and as such should be able to be integrated into tests.

The compiler errors are saved in hc_\<originalHeaderFileName\>.h.log.
