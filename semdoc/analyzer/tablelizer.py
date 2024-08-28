from copy import deepcopy, copy
from semdoc import logging
from semdoc.structure import ElementType as ET, Element

logger = logging.getLogger("semdoc.analyzer.tablelizer")


class Tablelizer:
    def __init__(self):
        self.name = "Tablelizer"

    def find_tables(self, structure):
        for element in structure.children:
            if element.category == ET.Table:
                yield element
            else:
                yield from self.find_tables(element)

    def tabelize(self, table):
        logger.debug(f"working on table in {table.region()}")

        # delete everything but text lines and flatten the structure
        text_lines = list(
            table.iter_children(filter=lambda e: e.category == ET.TextLine)
        )
        table.children = []
        logger.debug(f"found {len(text_lines)} lines")

        columns: list[tuple[Region, set[Element]]] = []
        rows: list[tuple[Region, set[Element]]] = []
        for text_line in text_lines:
            region = text_line.region()
            logger.debug(f"sorting line in {region}")
            column = None
            for c, elmns in columns:
                if c.overlaps_x(region):
                    column = c
                    c.incorporate(region)
                    elmns.add(text_line)
                    logger.debug(f"belongs to columns {elmns} in {column}")
                    break
            if not column:
                logger.debug("seems to belong to new column")
                column = copy(region)
                columns.append((column, {text_line}))

            row = None
            for r, elmns in rows:
                if r.overlaps_y(region):
                    row = r
                    row.incorporate(region)
                    elmns.add(text_line)
                    logger.debug(f"belongs to row {elmns} in {row}")
                    break
            if not row:
                logger.debug("seems to belong to new row")
                row = copy(region)
                rows.append((row, {text_line}))

        columns.sort(key=lambda c: c[0].x)
        rows.sort(key=lambda r: r[0].y)
        logger.debug(f"found {len(columns)} columns and {len(rows)} rows")

        for column_region, _ in columns:
            column_region.y = table.region().y
            column_region.height = table.region().height
        for row_region, row_lines in rows:
            logger.debug(f"working on row {row_region}")
            region.x = table.region().x
            region.width = table.region().width
            row = Element(ET.TableRow)
            row.set_property("region", row_region, self.name)
            table.add(row)
            for column_region, col_lines in columns:
                logger.debug(f"looking at column {column_region}")
                cell_region = row_region.intersection(column_region)
                logger.debug(f"new cell region is {cell_region}")
                cell_lines = row_lines.intersection(col_lines)
                cell = Element(ET.TableCell)
                cell.set_property("region", cell_region, self.name)
                row.add(cell)
                for line in cell_lines:
                    cell.add(line)

        logger.debug(f"now table is {table}")

    def run(self, structure):
        out = deepcopy(structure)
        for table in self.find_tables(out):
            self.tabelize(table)
        return out
