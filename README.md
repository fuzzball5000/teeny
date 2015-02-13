Teeny hasher, by Gary Richardson.

Teeny hasher is a small Python script, designed to iterate through a directory structure and produce a unique hash value based on the file contents and paths of certain files. The tool operates on the principle of a Merkle tree; if any end node in the tree changes, the resultant hash value is changed. Path and hash information is stored in an XML file, which must be secured against unauthorised tampering. 

Usage:

Teeny stores it’s configuration in an ini file, which must be readable by the same user which is executing Teeny.py:

[DEFAULT]
output = /home/someuser **output path for XML file**
path = /eg/path/I/care/about,/another/path/I/care/about **paths to scan CSV**
include = jpeg,doc,class,exe **file types to include CSV, do not place file types in quotes**

Teeny supports two methods of execution:

To generate a new hash or hashes:

$ python ./teeny.py --ini /path/to/teeny.ini --generate 

Teeny iterates through the given paths, loads each file into memory (in 4mb chunks) and produces a hash value of the file contents and paths, which are then stored in the XMLS file. 

To compare an existing hash or hashes:

$ python ./teeny.py --ini /path/to/teeny.ini --compare

Teeny will, for each path defined in the ini, compare hashes of those paths to those stored in the XML file and if correct will generate an informational syslog message to the locally defined syslog server. If the generated and stored hashes for any given path differ, then a warning will be logged to syslog - It will also generate and store a Linux ls -alrtRL output in the XML file’s directory for the path in question to assist with finding which files may have been modified.

Teeny also checks for invalid paths, invalid XML files, or bad XML file paths. If any of these errors are encountered, Teeny will generate an error to the syslog. 
