"""
MxGraph Primitives
<move x="0" y="0"/>
<line x="0" y="0"/>
<quad x1="0" y1="0" x2="0" y2="0"/>
<curve x1="0" y1="0" x2="0" y2="0" x3="0" y3="0"/>
Updated with changed from https://gist.github.com/dabenny
"""
from xml.dom import minidom
import re


def create_constraint(document, parent, x, y, perimeter=1):
    """ Create a constraint """
    constraint = document.createElement('constraint')
    constraint.setAttribute('x', str(x))
    constraint.setAttribute('y', str(y))
    constraint.setAttribute('perimeter', str(perimeter))
    parent.appendChild(constraint)


def create_connections(document, parent, nx=3, ny=3):
    """ Create connections """
    connections = document.createElement('connections')
    parent.appendChild(connections)

    nx += 1
    ny += 1
    for x in [1/nx*n for n in range(1, nx)]:
        create_constraint(document, connections, 0, x)
        create_constraint(document, connections, 1, x)
        create_constraint(document, connections, x, 0)
        create_constraint(document, connections, x, 1)


def create_move(document, parent, x, y):
    """ Move to a specified point """
    move = document.createElement('move')
    move.setAttribute('x', str(x))
    move.setAttribute('y', str(y))
    parent.appendChild(move)


def create_line(document, parent, x, y):
    """ Create a line from the current position. """
    line = document.createElement('line')
    line.setAttribute('x', str(x))
    line.setAttribute('y', str(y))
    parent.appendChild(line)


def create_curve(document, parent, x1, y1, x2, y2, x3, y3):
    """ Create a cubic curve from the current position. """
    curve = document.createElement('curve')
    curve.setAttribute('x1', str(x1))
    curve.setAttribute('y1', str(y1))
    curve.setAttribute('x2', str(x2))
    curve.setAttribute('y2', str(y2))
    curve.setAttribute('x3', str(x3))
    curve.setAttribute('y3', str(y3))
    parent.appendChild(curve)


def create_quad(document, parent, x, y, via_x, via_y):
    """ Create a quadratic curve from the current position.
    Attracts curve to the specified via point.
    """
    quad = document.createElement('quad')
    quad.setAttribute('x', str(x))
    quad.setAttribute('y', str(y))
    quad.setAttribute('x1', str(via_x))
    quad.setAttribute('y1', str(via_y))
    parent.appendChild(quad)


def create_arc(document, parent, rx, ry, rotation, flag1, flag2, x, y):
    """ Create an elliptical arc from the current position. """
    arc = document.createElement('arc')
    arc.setAttribute('rx', str(rx))
    arc.setAttribute('ry', str(ry))
    arc.setAttribute('rotation', str(rotation))
    arc.setAttribute('flag1', str(flag1))
    arc.setAttribute('flag2', str(flag2))
    arc.setAttribute('x', str(x))
    arc.setAttribute('y', str(y))
    parent.appendChild(arc)

def process_rect(document, parent, rect):
    """ Process a rectangle """
    rectangle = document.createElement('rect')
    rectangle.setAttribute('x', rect.getAttribute('x'))
    rectangle.setAttribute('y', rect.getAttribute('y'))
    rectangle.setAttribute('width', rect.getAttribute('width'))
    rectangle.setAttribute('height', rect.getAttribute('height'))
    parent.appendChild(rectangle)
    parent.appendChild(document.createElement('stroke'))


def process_polygon(document, parent, polygon):
    """ Process a polygon """
    points = polygon.getAttribute('points').split(' ')
    points = zip(*(iter(points),) * 2)
    path = document.createElement('path')
    parent.appendChild(path)
    move = document.createElement('move')
    p = next(points)
    move.setAttribute('x', p[0])
    move.setAttribute('y', p[1])
    path.appendChild(move)
    for (x, y) in points:
        line = document.createElement('line')
        line.setAttribute('x', x)
        line.setAttribute('y', y)
        path.appendChild(line)
    parent.appendChild(document.createElement('stroke'))


def process_line(document, parent, line):
    """ Process a line """
    x1 = line.getAttribute('x1')
    y1 = line.getAttribute('y1')
    x2 = line.getAttribute('x2')
    y2 = line.getAttribute('y2')
    path = document.createElement('path')
    parent.appendChild(path)
    move = document.createElement('move')
    move.setAttribute('x', x1)
    move.setAttribute('y', y1)
    path.appendChild(move)
    line = document.createElement('line')
    line.setAttribute('x', x2)
    line.setAttribute('y', y2)
    path.appendChild(line)
    parent.appendChild(document.createElement('stroke'))


def process_circle(document, parent, circle):
    """ Process a circle """
    cx = circle.getAttribute('cx')
    cy = circle.getAttribute('cy')
    r = circle.getAttribute('r')
    ellipse = document.createElement('ellipse')
    ellipse.setAttribute('h', r)
    ellipse.setAttribute('w', r)
    ellipse.setAttribute('x', cx)
    ellipse.setAttribute('y', cy)
    parent.appendChild(ellipse)
    parent.appendChild(document.createElement('stroke'))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def process_path(document, parent, path):
    """ Process a path """
    d = path.getAttribute('d')
    path = document.createElement('path')
    matches = [u.group() for u in re.finditer(
        r"[a-zA-Z,]|-?(?:\d+\.\d+(?:e-?\d+)?|\.\d+(?:e-?\d+)?|\d+(?:e-?\d+)?)(?!=\d)", d)
               if u.group() != ',']
    x0, y0 = 0, 0
    xs, ys = 0, 0
    while matches:
        if re.match(r"[Mm]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            while matches and is_number(matches[0]):
                x = float(matches.pop(0)) + (x0 if relative else 0)
                y = float(matches.pop(0)) + (y0 if relative else 0)
                create_move(document, path, x, y)
                x0 = x
                y0 = y
                xs = x0
                ys = y0
        elif re.match(r"[Cc]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            while matches and is_number(matches[0]):
                x1 = float(matches.pop(0)) + (x0 if relative else 0)
                y1 = float(matches.pop(0)) + (y0 if relative else 0)
                x2 = float(matches.pop(0)) + (x0 if relative else 0)
                y2 = float(matches.pop(0)) + (y0 if relative else 0)
                x = float(matches.pop(0)) + (x0 if relative else 0)
                y = float(matches.pop(0)) + (y0 if relative else 0)
                create_curve(document, path, x1, y1, x2, y2, x, y)
                x0 = x
                y0 = y
        elif re.match(r"[Ss]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            while matches and is_number(matches[0]):
                x2 = float(matches.pop(0)) + (x0 if relative else 0)
                y2 = float(matches.pop(0)) + (y0 if relative else 0)
                x = float(matches.pop(0)) + (x0 if relative else 0)
                y = float(matches.pop(0)) + (y0 if relative else 0)
                create_curve(document, path, x2, y2, x2, y2, x, y)
                x0 = x
                y0 = y
        elif re.match(r"[Ll]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            x = float(matches.pop(0)) + (x0 if relative else 0)
            y = float(matches.pop(0)) + (y0 if relative else 0)
            create_line(document, path, x, y)
            x0 = x
            y0 = y
        elif re.match(r"[Hh]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            x = float(matches.pop(0)) + (x0 if relative else 0)
            create_line(document, path, x, y0)
            x0 = x
        elif re.match(r"[Vv]", matches[0]):
            command = matches.pop(0)
            relative = command.islower()
            y = float(matches.pop(0)) + (y0 if relative else 0)
            create_line(document, path, x0, y)
            y0 = y
        elif re.match(r"[Zz]", matches[0]):
            command = matches.pop(0)
            create_line(document, path, xs, ys)
            x0 = xs
            y0 = ys

        else:
            print("Error", matches.pop(0))
    parent.appendChild(path)
    parent.appendChild(document.createElement('stroke'))


def process_group(document, parent, group):
    """ Process a group """
    for child in group.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue

        if child.tagName == 'g':
            process_group(document, parent, child)
        elif child.tagName == 'polygon':
            process_polygon(document, parent, child)
        elif child.tagName == 'line':
            process_line(document, parent, child)
        elif child.tagName == 'rect':
            process_rect(document, parent, child)
        elif child.tagName == 'circle':
            process_circle(document, parent, child)
        elif child.tagName == 'path':
            process_path(document, parent, child)


def process_svg(svg_string):
    """ Process an SVG file """
    file = minidom.parseString(svg_string)
    svg = file.getElementsByTagName('svg')[0]
    view_box = svg.getAttribute('viewBox').split(' ')
    width, height = float(view_box[2]), float(view_box[3])

    document = minidom.Document()
    shape = document.createElement('shape')
    shape.setAttribute('aspect', 'variable')  # or fixed
    shape.setAttribute('h', view_box[2])
    shape.setAttribute('w', view_box[3])
    shape.setAttribute('strokewidth', "inherit")

    parent = document.appendChild(shape)

    create_connections(document, parent)

    background = document.createElement('background')
    rect = document.createElement('rect')
    rect.setAttribute('x', view_box[0])
    rect.setAttribute('y', view_box[1])
    rect.setAttribute('w', view_box[2])
    rect.setAttribute('h', view_box[3])
    background.appendChild(rect)
    foreground = document.createElement('foreground')
    foreground.appendChild(document.createElement('fillstroke'))
    shape.appendChild(background)
    shape.appendChild(foreground)

    process_group(document, foreground, svg)
    return document.toprettyxml()