#!/bin/bash
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Eugene Frolov <eugene@frolov.net.ru>
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

set -x

WEB_HOST=10.0.0.11
WEB_USER=packages

RSA_KEY="/var/lib/jenkins/.ssh/web_rsa"

GERRIT_PROJECT=${GERRIT_PROJECT:-"labs/restalchemy"}
GERRIT_CHANGE_NUMBER=${GERRIT_CHANGE_NUMBER:-"1"}
GERRIT_PATCHSET_NUMBER=${GERRIT_PATCHSET_NUMBER:-"1"}
GERRIT_BRANCH=${GERRIT_BRANCH:-master}
GERRIT_EVENT_TYPE=${GERRIT_EVENT_TYPE:-"change-merged"}


WORKSPACE_ROOT="~/labs"
PROJECT_ROOT=$WORKSPACE_ROOT/$GERRIT_PROJECT

ALL_PKG_DIR="$PROJECT_ROOT/all"
BRANCH_PKG_DIR="$PROJECT_ROOT/merged/branch"
PACHSET_IN_BRANCH_PKG_DIR="$PROJECT_ROOT/merged/patchset"
PACHSET_PKG_ROOT="$PROJECT_ROOT/patchset"

BUILDED_PKG_DIR="./dist"


function dst_command {
    COMMAND=$1

    RESULT=$(ssh -i $RSA_KEY $WEB_USER@$WEB_HOST "$COMMAND")
}

function init_dst_host {

    dst_command "ls -l $PROJECT_ROOT" || dst_command "mkdir -p $PROJECT_ROOT" && \
    dst_command "ls -l $ALL_PKG_DIR" || dst_command "mkdir -p $ALL_PKG_DIR" && \
    dst_command "ls -l $BRANCH_PKG_DIR" || dst_command "mkdir -p $BRANCH_PKG_DIR" && \
    dst_command "ls -l $PACHSET_PKG_ROOT" || dst_command "mkdir -p $PACHSET_PKG_ROOT" && \
    dst_command "ls -l $PACHSET_IN_BRANCH_PKG_DIR" || dst_command "mkdir -p $PACHSET_IN_BRANCH_PKG_DIR"
}

function get_packet_filename {
    PKG_DIR=$1
    RESULT=$(ls -t1 $PKG_DIR | head -1)
}

function upload_packet {
    SRC_FILE="$BUILDED_PKG_DIR/$1"
    DST_FILE="$ALL_PKG_DIR/$1"
    scp -i $RSA_KEY $SRC_FILE $WEB_USER@$WEB_HOST:$DST_FILE
}

function build_package {
    # Build package
    python setup.py build
    python setup.py sdist
}

function create_link {
    dst_command "readlink -e $ALL_PKG_DIR/$1"
    SRC_PKG_FILENAME=$RESULT

    DST="$PACHSET_PKG_ROOT/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER"
    dst_command "mkdir -p $DST"
    dst_command "ln -s $SRC_PKG_FILENAME $DST/$1"

    if [[ "$GERRIT_EVENT_TYPE" == "change-merged" ]]; then

        DST="$PACHSET_IN_BRANCH_PKG_DIR/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER"
        dst_command "mkdir -p $DST"
        dst_command "ln -s $SRC_PKG_FILENAME $DST/$1"

        DST="$BRANCH_PKG_DIR/$GERRIT_BRANCH"
        dst_command "mkdir -p $DST"
        dst_command "rm -rf $DST/*"
        dst_command "ln -s $SRC_PKG_FILENAME $DST/$1"
    fi
}

init_dst_host

build_package

get_packet_filename $BUILDED_PKG_DIR
PKG_FILENAME=$RESULT

upload_packet $PKG_FILENAME

create_link $PKG_FILENAME
