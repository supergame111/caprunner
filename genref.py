#!python

import os, json
from optparse import OptionParser

from caprunner.exportfile import ExportFile
from caprunner.refcollection import refCollection

def process(exp, options):
    if options.pretty_print:
        exp.pprint()
    return refCollection.from_export_file(exp).export()

def main():
    parser = OptionParser(usage = "usage: %prog [options] PATH [PATH...]",
                          description = """\
This will process export file as generated by the Javacard converter.

The given path will be processed depending if it is a directory or a file.
If a directory all the export file found in the directory will be processed.
""")

    parser.add_option("-d", "--dump",
                      help    = "Dump the processed result to a pickle file.")

    parser.add_option("-P", "--pretty-print", default=False,
                      action="store_true", help= "Pretty print the results")

    parser.add_option("-v", "--verbose", default=False, action="store_true")

    parser.add_option("-i", "--impoort", help = "Import the dumped file")

    (options, args) = parser.parse_args()

    if options.impoort:
        f = open(options.impoort)
        s = json.loads(f.read())
        for pkg in s:
            refCollection.impoort(pkg)
        print "Import sucessfull !"
        return

    if len(args) == 0:
        parser.print_help()
        return

    res = []

    for path in args:
        if os.path.isdir(path):
            for dirname, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.exp'):
                        if options.verbose: print "Processing %s" % os.path.join(dirname, filename)
                        # Good to go !
                        f = open(os.path.join(dirname, filename))
                        exp = ExportFile(f.read())
                        refs = process(exp, options)
                        res.append(refs)
        else:
            f = open(path)
            exp = ExportFile(f.read())
            refs = process(exp, options)
            res.append(refs)
    if options.dump is not None:
        f = open(options.dump, 'wb')
        f.write(json.dumps(res))

main()
