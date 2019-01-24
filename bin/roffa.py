from typing import Optional

import roffa
import click
import logging
import re

logger = logging.getLogger('roffa')

REGEX_DURATION = re.compile(r"^\s*(?:(?P<hours>\d+)h)?\s*(?:(?P<minutes>\d+)m)?\s*(?:(?P<seconds>\d+)s)?\s*$")

verbose_parsed = False
current_level = logging.FATAL


def set_verbose(_, __, value):
    global current_level

    loglevel = logging.INFO

    if value:
        loglevel = logging.DEBUG

    if current_level > loglevel:
        current_level = loglevel
        logging.basicConfig(level=loglevel)


def verbose():
    return click.option('--verbose', '-v', is_flag=True, callback=set_verbose, is_eager=True, expose_value=False,
                        help="Enable verbose logging")


def parse_time(dur_str: str) -> Optional[int]:
    match = REGEX_DURATION.match(dur_str)

    if not match:
        return None

    return (((int(match.group('hours') or 0) * 60) + int(match.group('minutes') or 0)) * 60) + int(
        match.group('seconds') or 0)


def validate_interval(ctx, param, value):
    if str(value).strip() == "":
        raise click.BadParameter('interval can not be empty')

    parsed = parse_time(value)

    if parsed is None:
        raise click.BadParameter('interval can\'t be parsed: {}'.format(value))

    logger.debug('Parsed string interval {} to {} seconds'.format(value, parsed))

    return parsed


@click.group()
@verbose()
def cli():
    pass


@cli.command()
@click.option('--interval', '-w', default="1m", callback=validate_interval,
              help="At which interval the daemon should enforce state,"
                   + "format is [<hours>h][<minutes>m][<seconds>s], aka 3h, or 30s",
              show_default=True, )
@click.option('--once', '-1', is_flag=True, help="Enforce state once and exit")
@click.option('--config', '-c', default="/etc/roffa/main.yml", type=click.File('rb'), help="Location of roffa config",
              show_default=True)
@click.option('--dry-run', '--dryrun', '--noop', '-n', 'dryrun', is_flag=True, help="Run in dry-run or no-op mode")
@verbose()
def daemon(**kwargs):
    roffa_inst = roffa.Roffa.from_args(**kwargs)
    roffa_inst.run()


if __name__ == '__main__':
    cli()
