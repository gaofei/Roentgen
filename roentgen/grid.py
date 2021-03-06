"""
Icon grid drawing.

Author: Sergey Vartanov (me@enzet.ru).
"""
import numpy as np
from colour import Color
from svgwrite import Drawing
from typing import List, Dict, Any, Set

from roentgen.icon import Icon, IconExtractor
from roentgen.scheme import Scheme


def draw_all_icons(output_file_name: str, columns: int = 16, step: float = 24):
    """
    Draw all possible icon combinations in grid.

    :param output_file_name: output SVG file name for icon grid
    :param columns: the number of columns in grid
    :param step: horizontal and vertical distance between icons
    """
    tags_file_name: str = "data/tags.yml"
    scheme: Scheme = Scheme(tags_file_name)

    to_draw: List[Set[str]] = []

    for element in scheme.icons:  # type: Dict[str, Any]
        if "icon" in element and set(element["icon"]) not in to_draw:
            to_draw.append(set(element["icon"]))
        if "add_icon" in element and set(element["add_icon"]) not in to_draw:
            to_draw.append(set(element["add_icon"]))
        if "over_icon" not in element:
            continue
        if "under_icon" in element:
            for icon_id in element["under_icon"]:  # type: str
                current_set = set([icon_id] + element["over_icon"])
                if current_set not in to_draw:
                    to_draw.append(current_set)
        if not ("under_icon" in element and "with_icon" in element):
            continue
        for icon_id in element["under_icon"]:  # type: str
            for icon_2_id in element["with_icon"]:  # type: str
                current_set: Set[str] = set(
                    [icon_id] + [icon_2_id] + element["over_icon"])
                if current_set not in to_draw:
                    to_draw.append(current_set)
            for icon_2_id in element["with_icon"]:  # type: str
                for icon_3_id in element["with_icon"]:  # type: str
                    current_set = set(
                        [icon_id] + [icon_2_id] + [icon_3_id] +
                        element["over_icon"])
                    if (icon_2_id != icon_3_id and icon_2_id != icon_id and
                            icon_3_id != icon_id and
                            current_set not in to_draw):
                        to_draw.append(current_set)

    icons_file_name: str = "icons/icons.svg"
    extractor: IconExtractor = IconExtractor(icons_file_name)

    specified_ids: Set[str] = set()

    for icons_to_draw in to_draw:  # type: List[str]
        specified_ids |= icons_to_draw
    print(
        "Icons with no tag specification: \n    " +
        ", ".join(sorted(extractor.icons.keys() - specified_ids)) + ".")

    draw_grid(output_file_name, to_draw, extractor, columns, step)


def draw_grid(
        file_name: str, combined_icon_ids: List[Set[str]],
        extractor: IconExtractor, columns: int = 16, step: float = 24,
        color=Color("#444444")):
    """
    Draw icons in the form of table

    :param file_name: output SVG file name
    :param combined_icon_ids: list of set of icon string identifiers
    :param extractor: icon extractor that generates icon SVG path commands using
        its string identifier
    :param columns: number of columns in grid
    :param step: horizontal and vertical distance between icons in grid
    :return:
    """
    point: np.array = np.array((step / 2, step / 2))
    width: float = step * columns
    number: int = 0
    icons: List[List[Icon]] = []

    for icons_to_draw in combined_icon_ids:  # type: Set[str]
        found: bool = False
        icon_set: List[Icon] = []
        for icon_id in icons_to_draw:  # type: str
            icon, extracted = extractor.get_path(icon_id)  # type: Icon, bool
            assert extracted, f"no icon with ID {icon_id}"
            icon_set.append(icon)
            found = True
        if found:
            icons.append(icon_set)
            number += 1

    height: int = int(int(number / (width / step) + 1) * step)
    svg: Drawing = Drawing(file_name, (width, height))
    svg.add(svg.rect((0, 0), (width, height), fill="#FFFFFF"))

    for combined_icon in icons:  # type: List[Icon]
        background_color = "#FFFFFF"
        svg.add(svg.rect(
            point - np.array((-10, -10)), (20, 20),
            fill=background_color))
        for icon in combined_icon:  # type: Icon
            path = icon.get_path(svg, point)
            path.update({"fill": color.hex})
            svg.add(path)
        point += np.array((step, 0))
        if point[0] > width - 8:
            point[0] = step / 2
            point += np.array((0, step))
            height += step

    print(f"Icons: {number}.")

    with open(file_name, "w") as output_file:
        svg.write(output_file)
