FROM python:3.8.18-slim-bullseye
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
EXPOSE 8200

RUN apt-get update -y && apt install -y nano

RUN apt-get update -y
RUN apt-get install ffmpeg libsm6 libxext6 libzbar0 -y

RUN pip3 install torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html

RUN pip3 install matplotlib>=3.2.2 numpy>=1.18.5 opencv-python>=4.1.1 Pillow>=7.1.2 PyYAML>=5.3.1 requests>=2.23.0 scipy>=1.4.1 tqdm>=4.64.0 pandas>=1.1.4 seaborn>=0.11.0 tensorboard>=2.4.1 psutil  thop>=0.1.1 

RUN apt update && apt install -y zip htop screen libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 redis-server

RUN python -m pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]
