import click
import sys

from . import process_svg

@click.command()
@click.argument('svg_file', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def main(svg_file, output):
    """ Convert SVG to mxGraph XML """
    content = svg_file.read()
    output.write(process_svg(content))


if __name__ == '__main__':
    main()