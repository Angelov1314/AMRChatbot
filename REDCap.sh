#!/bin/sh
DATA="token=DEA725B26FA25881CA4707FA7130C374&content=record&format=json&type=flat&data=[{\"record_id\":\"456789\"}]"

CURL=`which curl`
$CURL -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Accept: application/json" \
      -X POST \
      -d $DATA \
      https://redcap.oucru.org/redcap/api/