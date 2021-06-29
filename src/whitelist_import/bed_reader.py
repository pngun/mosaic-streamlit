import re

import pandas as pd

from .columns import ALLELE_INFO, CHROM, END, START
from .whitelist import Whitelist

__all__ = ["BedReader"]

ALLELE_INFO_RE = re.compile("([A-Z]*)[->]([A-Z]*)")
DESIGNER_RULE_RE = re.compile(r"chr(?:omosome)?([^:]+):(\d+)-(\d+)", re.IGNORECASE)
ROW_TYPE = "row_type"


class BedReader:
    """Reader for BED files

    Assumes tab separated file where first three rows correspond to
    name, start position and end position
    """

    def read(self, filename):
        """Read whitelist from .bed file

        Args:
            filename: str

        Raises:
            ValueError: Unsupported file format

        Returns:
            Whitelist
        """
        if filename.endswith(".bed"):
            return self.__read_bed(filename)
        elif filename.endswith(".csv"):
            return self.__read_designer(filename)
        else:
            raise ValueError(f"Unsupported file format {filename}")

    def validate(self, filename):
        """Checks whether filename is a valid whitelist

        Args:
            filename: str
                path to whitelist file to validate

        Returns:
            bool: True when filename is a valid whitelist
        """
        try:
            self.read(filename)
            return True
        except Exception:
            return False

    def __read_bed(self, filename):
        df = pd.read_csv(filename, sep=r"\s+", header=None, converters={0: parse_chromosome, 1: parse_int, 2: parse_int, 3: parse_allele}).rename(columns={0: CHROM, 1: START, 2: END, 3: ALLELE_INFO})

        return Whitelist(df)

    def __read_designer(self, filename):
        df = pd.read_csv(filename, sep=",", header=None, converters={2: parse_allele}).rename(columns={0: "row_type", 1: "variant", 2: ALLELE_INFO})

        if len(df.columns) < 2:
            raise ValueError("Invalid whitelist")

        if ALLELE_INFO not in df.columns:
            df[ALLELE_INFO] = None

        whitelist = []
        for row in df.itertuples():
            if row.row_type.lower() != "region":
                continue

            match = DESIGNER_RULE_RE.match(row.variant)
            if not match:
                raise ValueError(f"Could not parse {row.variant}")

            whitelist.append([match.group(1), int(match.group(2)), int(match.group(3)), getattr(row, ALLELE_INFO)])  # chromosome  # start  # end  # allele info

        return Whitelist(pd.DataFrame(whitelist, columns=[CHROM, START, END, ALLELE_INFO]))


def parse_int(value: str):
    """Converter for int columns"""  # noqa
    return int(value.strip())


def parse_chromosome(value: str):
    """Converter for CHROM column

    removes chr prefix is present
    """  # noqa
    value = value.strip()
    if value.startswith("chr"):
        return value[3:]
    else:
        return value


def parse_allele(value: str):
    """Converter for (optional) allele info

    Converts allele specification into FROM-TO format
    """  # noqa
    match = ALLELE_INFO_RE.match(value)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None
