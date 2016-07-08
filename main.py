"""Entry point for the Tidal Disruption Catalog
"""


def main(args, clargs, log):
    from .tidaldisruptioncatalog import TidalDisruptionCatalog

    # Load tidal disruption-specific command-line argumenets
    # (adding them to existing settings)
    args = load_command_line_args(args=args, clargs=clargs)
    if args is None:
        return

    catalog = TidalDisruptionCatalog(args, log)

    if args.subcommand == 'import':
        log.info("Running `importer`.")
        catalog.import_data()

    return


def load_command_line_args(args=None, clargs=None):
    """Load and parse command-line arguments.
    """
    import argparse
    from astrocats.catalog.main import add_parser_arguments

    parser = argparse.ArgumentParser(prog='tidaldisruptions',
                                     description='The Open Tidal Disruption '
                                     'Event Catalog.')

    subparsers = parser.add_subparsers(
        description='valid subcommands', dest='subcommand')
    # `import` --- importing tidal disruption data
    import_pars = subparsers.add_parser("import",
                                        help="Import tidal disruption data.")

    return add_parser_arguments(parser, import_pars, args, clargs)
