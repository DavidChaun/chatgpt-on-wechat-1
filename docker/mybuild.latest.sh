#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/MyDockerfile.latest \
             -t wei/chatgpt-on-wechat .

docker tag wei/chatgpt-on-wechat wei/chatgpt-on-wechat:$(date +%y%m%d)