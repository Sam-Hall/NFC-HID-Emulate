#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# singleprocess.py - simple cross platform module to ensure only one instance of the script runs at a time
#
# Windows will use a named mutex, other platforms will use a pid file in the temp directory
#


import sys
import os
import tempfile


class AlreadyLocked(Exception):
    """Requested lock unavailable"""
    def __init__(self, *args):
        Exception.__init__(self, "Requested lock not available", *args)


def create_lock(lock_name):
    if sys.platform.startswith('win32'):
        import namedmutex
        lock_object = namedmutex.NamedMutex(lock_name)
        try:
            acquired = lock_object.acquire(0.001)
        except WindowsError:
            acquired = False
        if not acquired:
            raise AlreadyLocked
    else:
        import fcntl
        pid = str(os.getpid())
        pid_file = tempfile.gettempdir() + os.sep + lock_name + '.pid'
        if os.path.isfile(pid_file):
            try:
                # read the old pid - which should be locked
                lock_object = open(pid_file, 'r')
                fcntl.flock(lock_object, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # lock_object.seek(0)
                # old_pid = lock_object.readline()
                lock_object.close()
            except IOError:
                raise AlreadyLocked
        # (re-)create a pid file
        file(pid_file, 'w').write(pid)
        lock_object = open(pid_file, 'r')
        fcntl.flock(lock_object, fcntl.LOCK_EX | fcntl.LOCK_NB)

    return lock_object


def unlock(lock_object):
    # close() just happens to work on both NamedMutex and File object types:
    if lock_object: lock_object.close()
