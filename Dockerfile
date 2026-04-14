FROM rbs-docker:works
RUN apt-get update && apt-get install -y portaudio19-dev
RUN pip install scipy numpy-quaternion pygame sounddevice
