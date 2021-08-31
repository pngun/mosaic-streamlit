import math
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def _normalize_variants(variants):
    return [var.replace(":", "-").replace("/", "-").replace("-*", "") for var in variants]


def _get_annotations(ids):
    url = "https://api.missionbio.io/annotations/v1/variants?ids=" + ",".join(ids)
    r = requests.get(url=url)
    return r.json()


def _chunks(variants):
    for i in range(0, len(variants), 100):
        yield variants[i : i + 100]


def get_annotations_from_api(variants):
    variants = _normalize_variants(variants)
    workers = min(20, math.ceil(len(variants) / 100))
    data = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        items = {executor.submit(_get_annotations, ids): ids for ids in _chunks(variants)}
        for future in as_completed(items):
            # if there is an Exception let it propagate.
            # we assume that that means there is no internet
            item = future.result()
            data.extend(item)

    return data
