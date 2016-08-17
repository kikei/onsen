#!/bin/sh

PGDUMP=pg_dump
DBNAME=onsen
OUTPUT=${DBNAME}_backup-$(date +%Y%m%d).dump
TABLES="database_onsen database_entrypoint"

if [ $# = 1 ]; then
  OUTPUT=$1
  shift
fi

setup_outdir() {
  mkdir -p $(dirname $OUTPUT)
}

exec_backup() {
  tables=""
  while [ "X$1" != "X" ]; do
    tables="$tables -t $1"
    shift
  done
  $PGDUMP -a -d $DBNAME $tables > $OUTPUT
}

setup_outdir 

echo "Running backup > $OUTPUT"
exec_backup $TABLES
if [ $? = 0 ]; then
  echo "successfully done!"
fi
exit $?
