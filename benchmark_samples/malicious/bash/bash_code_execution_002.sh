#!/bin/bash
# Command injection
eval "$INPUT"
bash -c "$COMMAND"
