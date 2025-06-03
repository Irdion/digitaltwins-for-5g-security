FROM envoyproxy/envoy:v1.33.0

# install LuaRocks and build deps
RUN apt-get update \
  && apt-get install -y luarocks lua5.1-dev liblua5.1-dev \
  && luarocks install lua-cjson

# (optional) verify install
RUN lua -e "local cjson = require 'cjson'; print(cjson.decode('{\"x\":1}').x)"