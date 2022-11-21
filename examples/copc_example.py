from dataplug import CloudObject
from dataplug.geospatial.copc import CloudOptimizedPointCloud, copc_square_split_strategy

import logging
import laspy
from dataplug.util import setup_logging

setup_logging(logging.INFO)

if __name__ == '__main__':
    # Localhost minio config
    local_minio = {
        'aws_access_key_id': 'minioadmin',
        'aws_secret_access_key': 'minioadmin',
        'region_name': 'us-east-1',
        'endpoint_url': 'http://192.168.1.110:9000',
        'botocore_config_kwargs': {'signature_version': 's3v4'},
        'role_arn': 'arn:aws:iam::123456789012:role/S3Access',
        'use_token': True
    }

    co = CloudObject.from_s3(CloudOptimizedPointCloud,
                             's3://geospatial/copc/cnig/PNOA_2016_CAT_324-4570_ORT-CLA-COL.laz',
                             s3_config=local_minio)
    slices = co.partition(copc_square_split_strategy, num_chunks=9)

    for i, data_slice in enumerate(slices):
        las_data = data_slice.get()
        lidar_file = laspy.open(las_data)
        print(f'LiDAR slice #{i}:')
        print(f'Bounds: '
              f'({round(lidar_file.header.mins[0], 3)},{round(lidar_file.header.mins[1], 3)}) - '
              f'({round(lidar_file.header.maxs[0], 3)},{round(lidar_file.header.maxs[1], 3)})')
        print(f'Point count: {lidar_file.header.point_count}')
        print('---')
