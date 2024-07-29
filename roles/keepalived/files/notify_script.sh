#!/bin/sh

TYPE=$1
NAME=$2
STATE=$3

case "$STATE" in
"MASTER")
  systemctl start keepalived.target
  exit 0
  ;;
"BACKUP")
  systemctl stop keepalived.target
  exit 0
  ;;
"FAULT")
  systemctl stop keepalived.target
  exit 0
  ;;
*)
  echo "Unknown state"
  exit 1
  ;;
esac
