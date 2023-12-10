FROM python:3.11

RUN apt update && \
    apt install -y git libopencv-dev

RUN pip install --upgrade pip && \
    pip install matplotlib numpy ipykernel

CMD ["/bin/bash"]