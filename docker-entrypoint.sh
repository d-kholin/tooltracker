#!/bin/sh
set -e

# Fix /data ownership on every start — handles pre-existing volumes
# created before appuser ownership was established in the image.
chown -R appuser:appuser /data

exec gosu appuser "$@"
