# pyddsextractor

DDS Extractor using Python

## Make Environments

### Method 1 (required): Using Docker

Use `Docker Compose`.

Create an image and a container

```bash
cd docker/dev
docker compose up -d
```

Run bash in the container

```bash
cd docker/dev
docker compose exec dev main
# Or, docker exec -it <container_name or container_id> bash
```

### Method 2: Use venv

Python 3.11 or above is recommended.

1. Make venv
```bash
cd <this_project_root_dir>
# make venv
python3 -m venv .venv
```

2. Activate venv

On macOS/Linux,

```bash
source .venv/bin/activate
```

on Windows PowerShell or CMD,

```bash
.\venv\Scripts\activate
```

3. install requirements

Please run below in venv enviromnent.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

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