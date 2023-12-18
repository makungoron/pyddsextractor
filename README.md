# pyddsextractor

DDS Extractor using Python

## Make Environments

### Method 1 (required): Using Docker

### Method 2: Use venv


## How To Use

```
usage: ddsextractor.py [-h] --input INPUT --output OUTPUT

options:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        filepath to dds file
  --output OUTPUT, -o OUTPUT
                        output filepath
```

For example:

```bash
cd <this_project_root_dir>
python ddsextractor.py -i input.dds -o output.png
```

The format of the output file depends on the extension of output path.
Specify the extensions that can be used with `cv2.imwrite()`.