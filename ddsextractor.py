import argparse
import os

import numpy as np
import cv2

from src.dds import DDS


def main(input_filepath: str | os.PathLike,
         output_filepath: str | os.PathLike) -> None:
    dds = DDS(filepath=input_filepath)
    img = dds.decode()

    output_success = cv2.imwrite(output_filepath, img.astype(np.uint8))
    if output_success:
        print(f'[SUCCESS] File was saved at {output_filepath}')
    else:
        print('[FAILED] Output failed')


def set_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, type=str, help='filepath to dds file')
    parser.add_argument('--output', '-o', required=True, type=str, help='output filepath')
    return parser


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()
    main(args.input, args.output)
