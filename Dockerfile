FROM zauberzeug/nicegui:latest
RUN apt-get -y update && \
    apt upgrade -y && \
    apt-get install -y \
        git \
        curl
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ADD src/pomomural /app
CMD ["python3", "/app/main.py"]