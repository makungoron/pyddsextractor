import os
import struct
from pathlib import Path

import numpy as np


class DDS:
    HEADER_SIZE = 128
    WIDTH_OFFSET = 0x10
    HEIGHT_OFFSET = 0x0C
    FORMAT_OFFSET = 0x54

    HEADER_STRUCT = {
        'dwMagic': 'cccc',          # always 0x20534444 (' SDD')
        'dwSize': 'I',              # always 124
        'dwFlags': 'I',             # ヘッダ内の有効な情報 DDSD_* の組み合わせ
        'dwHeight': 'I',            # 画像の高さ x size
        'dwWidth': 'I',             # 画像の幅   y size
        'dwPitchOrLinearSize': 'I', # 横1 line の byte 数 (pitch) または 1面分の byte 数 (linearsize)
        'dwDepth': 'I',             # 画像の奥行き z size (Volume Texture 用)
        'dwMipMapCount': 'I',       # 含まれている mipmap レベル数
        'dwReserved1': 'I'*11,
        'dwPfSize': 'I',            # 常に 32
        'dwPfFlags': 'cccc',        # pixel フォーマットを表す DDPF_* の組み合わせ
        'dwFourCC': 'cccc',         # フォーマットが FourCC で表現される場合に使用する。 # DX10 拡張ヘッダが存在する場合は 'DX10' (0x30315844) が入る。
        'dwRGBBitCount': 'I',       # 1 pixel の bit 数
        'dwRBitMask': 'I',          # RGB format 時の mask
        'dwGBitMask': 'I',          # RGB format 時の mask
        'dwBBitMask': 'I',          # RGB format 時の mask
        'dwRGBAlphaBitMask': 'I',   # RGB format 時の mask
        'dwCaps': 'I',              # mipmap 等のフラグ指定用
        'dwCaps2': 'I',             # cube/volume texture 等のフラグ指定用
        'dwReservedCaps2': 'I'*2,
        'dwReserved2': 'I'
    }


    def __init__(self, filepath: str | os.PathLike) -> None:
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f'{filepath} is not exists, or not file')
        if self.filepath.is_dir():
            raise IsADirectoryError(f'{filepath} is a directory.')

        self.data: bytes = self.filepath.read_bytes()

        # Decoding header
        dds_header = struct.Struct('<' + ''.join(self.HEADER_STRUCT.values()))
        opts = dds_header.unpack_from(self.data, 0)
        self.opt = {}
        index = 0
        for key, format in self.HEADER_STRUCT.items():
            res = []
            for c in format:
                if c == 'c':
                    res.append(chr(int.from_bytes(opts[index])))
                else:
                    res.append(opts[index])
                index += 1
            if len(res) == 1:
                self.opt[key] = res[0]
            elif format in {'cccc', '4c'}:
                self.opt[key] = ''.join(res)
            else:
                self.opt[key] = res

        self._start_index = self.HEADER_SIZE + (20 if self.opt['dwFourCC'] == 'DX10' else 0)


    @property
    def header(self) -> bytes:
        return self.data[:self.HEADER_SIZE]


    @property
    def typeFormat(self) -> str:
        btype = self.data[self.FORMAT_OFFSET:self.FORMAT_OFFSET+4]
        return ''.join([chr(b) for b in btype])


    @property
    def width(self) -> int:
        return int.from_bytes(self.data[self.WIDTH_OFFSET:self.WIDTH_OFFSET+4], byteorder='little')


    @property
    def height(self) -> int:
        return int.from_bytes(self.data[self.HEIGHT_OFFSET:self.HEIGHT_OFFSET+4], byteorder='little')


    def decode(self) -> np.ndarray:
        fourcc = self.typeFormat
        if fourcc == 'BC4U':
            return self._decode_BC4U()
        else:
            raise NotImplementedError(f'{fourcc}')


    def _decode_BC4U(self):
        # decode all 4x4 block sequencially
        blocks = []
        for i in range(0, self.width * self.height // 2, 8):
            start_index = self._start_index + i
            block = self._decode_BC4U_block(self.data[start_index:start_index+8])
            blocks.append(block)

        # Combine each block into one ndarray
        s = np.array(blocks)
        n_blocks = self.width // 4
        hs = []
        for n in range(n_blocks):
            hs.append(np.hstack(s[n*256:n*256+256]))
        img = np.vstack(hs)
        return img


    def _decode_BC4U_block(self, block: bytes, verbose: bool = False) -> np.ndarray:
        """Decode a 4x4 block encoded by BC4 UNORM (BC4U).

        Args:
            block (bytes): bytes[8] object (4x4 pixels = 1 block)
            verbose (bool, optional): Show details to stdout. Defaults to False.

        Raises:
            ValueError: Invalid block object.

        Returns:
            numpy.ndarray: decoded pixels. The shape is 4x4.
        """
        if len(block) != 8:
            raise ValueError(f'block length is required 8, not {len(block)}.')
        alpha0 = block[0]
        alpha1 = block[1]
        if verbose:
            print('alpha 0:', alpha0)
            print('alpha 1:', alpha1)
        # NOTE: Loading data with little endian
        data =  block[6:8][::-1] + block[2:6][::-1]

        # convert data to 3[bit]x8[pixel]
        # NOTE: this method may cause low speed and require many memories.
        raw = ''.join([bin(t)[2:].zfill(8) for t in data])
        if verbose:
            print('raw:', ''.join([c+(' ' if i % 3 == 0 else '') for i, c in enumerate(raw, 1)]))
        pixels_bits = [int(raw[i:i+3], base=2) for i in range(0, len(raw), 3)]

        # BC4 UNORM interpolation
        colors = {}
        colors[0] = alpha0
        colors[1] = alpha1
        if alpha0 > alpha1:
            # 6 interpolated color values
            # for i in range(2, 8):
            #     colors[i] = (alpha0*(7-i+1) + alpha1*(i-1)) / 7
            colors[2] = (alpha0 * 6 + alpha1 * 1) / 7
            colors[3] = (alpha0 * 5 + alpha1 * 2) / 7
            colors[4] = (alpha0 * 4 + alpha1 * 3) / 7
            colors[5] = (alpha0 * 3 + alpha1 * 4) / 7
            colors[6] = (alpha0 * 2 + alpha1 * 5) / 7
            colors[7] = (alpha0 * 1 + alpha1 * 6) / 7
        else:
            # 4 interpolated color values
            # for i in range(2, 6):
            #     colors[i] = (alpha0*(5-i+1) + alpha1*(i-1)) / 5
            colors[2] = (alpha0 * 4 + alpha1 * 1) / 5
            colors[3] = (alpha0 * 3 + alpha1 * 2) / 5
            colors[4] = (alpha0 * 2 + alpha1 * 3) / 5
            colors[5] = (alpha0 * 1 + alpha1 * 4) / 5
            colors[6] = 0
            colors[7] = 255

        pixels = [colors[int(b)] for b in pixels_bits]
        pixels = pixels[8:][::-1] + pixels[:8][::-1]

        if verbose:
            print('pixels_bits:', pixels_bits)
            print(pixels)
        return np.array(pixels).reshape(4, 4).astype(np.uint8)