FROM python:3.10-slim-bookworm

WORKDIR /app
RUN pip install pyone
ADD https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64 /usr/sbin/dumb-init
RUN chmod +x /usr/sbin/dumb-init

COPY vmid-discover.py .

VOLUME ["/var/lib/cloud"]

ENTRYPOINT ["/usr/sbin/dumb-init", "--"]

CMD [ "python3", "vmid-discover.py" ]
