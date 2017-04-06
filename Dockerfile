FROM java:7-jre-alpine
ENV PACKAGES="\
  dumb-init \
  musl \
  linux-headers \
  build-base \
  bash \
  git \
  ca-certificates \
  python3 \
  python3-dev \
"

RUN echo \
  # replacing default repositories with edge ones
  && echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" > /etc/apk/repositories \
  && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
  && echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \

  # Add the packages, with a CDN-breakage fallback if needed
  && apk add --no-cache $PACKAGES || \
    (sed -i -e 's/dl-cdn/dl-4/g' /etc/apk/repositories && apk add --no-cache $PACKAGES) \
  && echo "http://dl-cdn.alpinelinux.org/alpine/v$ALPINE_VERSION/main/" > /etc/apk/repositories \

  # make some useful symlinks that are expected to exist
  && if [[ ! -e /usr/bin/python ]];        then ln -sf /usr/bin/python3 /usr/bin/python; fi \
  && if [[ ! -e /usr/bin/python-config ]]; then ln -sf /usr/bin/python3-config /usr/bin/python-config; fi \
  && if [[ ! -e /usr/bin/idle ]];          then ln -sf /usr/bin/idle3 /usr/bin/idle; fi \
  && if [[ ! -e /usr/bin/pydoc ]];         then ln -sf /usr/bin/pydoc3 /usr/bin/pydoc; fi \
  && if [[ ! -e /usr/bin/easy_install ]];  then ln -sf /usr/bin/easy_install-3* /usr/bin/easy_install; fi \

  # Install and upgrade Pip
  && easy_install pip \
  && pip install --upgrade pip \
  && if [[ ! -e /usr/bin/pip ]]; then ln -sf /usr/bin/pip3 /usr/bin/pip; fi

# Install application
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY consumer.py /app/

ONBUILD COPY . /app/
ONBUILD RUN chmod -R 755 /service/

CMD ["/usr/bin/python", "/app/consumer.py"]
#CMD ["/usr/bin/java", "-cp", \
#     "/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/jackson-core-2.1.1.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/commons-logging-1.1.1.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/jackson-databind-2.1.1.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/amazon-kinesis-client-1.2.1.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/jackson-annotations-2.1.1.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/aws-java-sdk-1.7.13.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/httpclient-4.2.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/commons-codec-1.3.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/httpcore-4.2.jar:/usr/local/lib/python2.7/dist-packages/amazon_kclpy-1.1.0-py2.7.egg/amazon_kclpy/jars/joda-time-2.4.jar:/code", \
#     "com.amazonaws.services.kinesis.multilang.MultiLangDaemon", \
#     "main.properties"]
