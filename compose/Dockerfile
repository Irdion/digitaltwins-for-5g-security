FROM envoyproxy/envoy:v1.33.0

RUN apt-get update \
  && apt-get install -y luarocks lua5.1-dev liblua5.1-dev \
  && luarocks install lua-cjson