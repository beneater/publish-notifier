import contextlib
import json
import socket
import time
import urllib2

import hipchat.config
import hipchat.room

import secrets

hipchat.config.token = secrets.hipchat_token


def hipchat_notify(room_id, message):
    # Pure kwargs don't work here because 'from' is a Python keyword...
    hipchat.room.Room.message(**{
        'room_id': room_id,
        'from': 'Publish Primate',
        'message': message,
        'color': 'purple',
    })


def get_version(url='http://www.khanacademy.org/api/v1/topicversion/default/id'):
    try:
        with contextlib.closing(urllib2.urlopen(url)) as f:
            data = json.loads(f.read())
    except urllib2.URLError, e:
        print "Couldn't get version: %s" % e
        if isinstance(e, urllib2.HTTPError):
            # When urlllib2 returns an HTTPError, the textual response returned
            # by read() can be helpful when debugging.
            print e.read()
        return None
    except socket.error, e:
        print "Couldn't get version: socket error %s" % e
        return None

    return data

def get_topicversion(version_num,
                     url='http://www.khanacademy.org/api/v1/topicversions'):
    try:
        with contextlib.closing(urllib2.urlopen(url)) as f:
            data = json.loads(f.read())
    except urllib2.URLError, e:
        print "Couldn't get version: %s" % e
        if isinstance(e, urllib2.HTTPError):
            # When urlllib2 returns an HTTPError, the textual response returned
            # by read() can be helpful when debugging.
            print e.read()
        return None
    except socket.error, e:
        print "Couldn't get version: socket error %s" % e
        return None

    for topicversion in data:
        if topicversion['number'] == version_num:
            return topicversion


def build_message(last_version, version):
    topicversion = get_topicversion(version)
    return ('Topic tree publish completed. Version %s -> %s<br>'
            '&bull; Title: %s<br>'
            '&bull; Description: %s<br>'
            '&bull; Last updated by: %s'
            % (last_version, version, topicversion['title'],
            topicversion['description'], topicversion['last_edited_by']))

if __name__ == '__main__':
    last_version = None

    while True:
        version = get_version()
        print version

        if version is not None:
            if last_version is not None and version != last_version:
                hipchat_notify(
                    secrets.hipchat_room_id,
                    build_message(last_version, version))
            last_version = version

        time.sleep(10)
