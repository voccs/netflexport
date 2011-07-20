from ConfigParser import ConfigParser
from optparse import OptionParser
from os.path import exists
from __init__ import Netflexport

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config", action="store",
                      type="string", help="Application settings file")
    parser.add_option("-r", "--ratings", dest="ratings", action="store",
                      type="string", help="File with list of rated IDs")
    (options, args) = parser.parse_args()

    if options.config is not None and exists(options.config): 
        config = ConfigParser()
        config.read(options.config)
    elif exists('./settings.cfg.local'):
        config = ConfigParser()
        config.read('./settings.cfg.local')
    else:
        raise Exception('No settings found!')

    export = Netflexport(config)
    export.export(options.ratings)

if __name__ == "__main__":
    main()
