"""Entry point for the Tidal Disruption Catalog
"""


def main(args, clargs, log):
    from .tidaldisruptioncatalog import TidalDisruptionCatalog
    from astrocats.catalog.argshandler import ArgsHandler

    # Create an `ArgsHandler` instance with the appropriate argparse machinery
    args_handler = ArgsHandler(log)
    # Parse the arguments to get the configuration settings
    args = args_handler.load_args(args=args, clargs=clargs)
    # Returns 'None' if no subcommand is given
    if args is None:
        return

    catalog = TidalDisruptionCatalog(args, log)

    # Run the subcommand given in `args`
    args_handler.run_subcommand(args, catalog)

    return
