import pandas as pd

from .columns import ALLELE_INFO, ALT, CHROM, END, POS, REF, START

__all__ = ["Whitelist"]


class Whitelist(pd.DataFrame):
    """Container for .bed file whitelist"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert CHROM in self.columns
        assert START in self.columns
        assert END in self.columns

        if ALLELE_INFO in self.columns:
            allele_info = self[ALLELE_INFO]

            def get_ref(info):
                if info is None:
                    return None
                return info.split("-")[0]

            def get_alt(info):
                if info is None:
                    return None
                return info.split("-")[1]

            self[REF] = allele_info.apply(get_ref)
            self[ALT] = allele_info.apply(get_alt)
        else:
            self[ALLELE_INFO] = None
            self[REF] = None
            self[ALT] = None

    @staticmethod
    def read(filename: str) -> "Whitelist":
        """Read whitelist from a bedfile

        Args:
            filename: str
                path to the bed file to read

        Returns:
            Whitelist
        """
        from missionbio.insights.data import BedReader

        return BedReader().read(filename)

    @property
    def filter_variants(self):
        """A filter function for an SNP DataFrame"""
        low = self[START].values  # noqa
        high = self[END].values
        chr = self[CHROM].values

        if ALLELE_INFO in self:
            allele_info = self[ALLELE_INFO].values
            ref = self[REF].values
            alt = self[ALT].values
        else:
            allele_info = ref = alt = None

        def whitelisted(v):
            return ((chr == v[CHROM]) & (low <= v[POS]) & (high >= v[POS]) & ((allele_info == None) | ((v[REF] == ref) & (v[ALT] == alt)))).any()  # noqa: E711

        return whitelisted
