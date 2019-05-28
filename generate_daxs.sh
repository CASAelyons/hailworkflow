#!/usr/bin/env bash

cd input
for f in *netcdf; do
$HAIL_WORKFLOW_DIR/run_casa_wf.sh $f
#sleep 2
done
