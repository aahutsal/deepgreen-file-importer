#!/usr/bin/python
# -*- coding: utf-8 -*-

from deepgreen_executor import *
from deepgreen_utils import *

import sys

def load_geojson_files(input_files):

    result = gpd.GeoDataFrame()
    for file_name in input_files:
        _gdf = gpd.read_file(file_name).to_crs(EPSG)
        file_datetime = get_datetime_from_file(file_name)
        _gdf.loc[:, 'datetime'] = file_datetime
        print(file_datetime, _gdf.shape)

        result = pd.concat(
            [
                _gdf,
                result
            ],
            axis='rows',
            ignore_index=True
        )
    # Normalize the index
    result.index = pd.Index([i for i in range(1, result.shape[0] + 1)])

    print(result.shape, result.datetime.unique(), result.head(2).T)

    return result


def load_data(from_cache=False):
    """
    Load data (polygons) to process and enrich via crawling
    :param from_cache: use cached pickle-files with geojons loaded
    :return: GeoPandasFrame
    """
    # file_for_processing = sys.argv[1]
    PATH = "/home/archer/dev/deepgreen-camel-clj/target/"
    # total_requests_to_process = -1
    # PATH = 'D:\WORK\Outsource\М1\deepgreen-file-importer\data'
    if from_cache:
        return pd.read_pickle(os.path.join(PATH, 'result.pkl'))
    else:
        return load_geojson_files(
            input_files=[
                # file_for_processing
                os.path.join(PATH, sys.argv[1]),
                # os.path.join(PATH, '2021_03_01.geojson'),
                # os.path.join(PATH, '2021_04_05.geojson'),
                # os.path.join(PATH, '2021_04_12.geojson')
            ]
        )


def enrich_data(gdf):
    """
    Start crawling and parsing
    :param gdf: GeoDataFrame. Geojons loaded
    :return: GeoDataFrame. Enriched with UkrForest API (LIAC)
    """
    return execute_enrichment(
        gdf,
        epsg=EPSG,
        limit=-1,
        chunk_size=10
    )


def save_data(gdf):
    """
    Save enriched data to PostgreSQL DB
    :param gdf: GeoDataFrame. Enriched with UkrForest API (LIAC)
    :return: Boolean
    """
    save_to_postgres(gdf, table_name=PG_TABLE_NAME)
    print('Data is saved. Please review the table [{}]'.format(PG_TABLE_NAME))


def start():
    """
    Main entry point
    :return: Boolean. True - success, False - error is happened
    """
    print(PG_TABLE_NAME)
    gdf = load_data(from_cache=False)
    gdf_enriched = enrich_data(gdf)
    save_data(gdf_enriched)


if __name__ == '__main__':
    start()
