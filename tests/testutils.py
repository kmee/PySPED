# -*- coding: utf-8 -*-
import fnmatch
import os

import pysped


def list_recursively(directory, pattern):
    """Returns files recursively from directory matching pattern
    :param directory: directory to list
    :param pattern: glob mattern to match
    """
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            # skip backup files
            if (filename.startswith('.#') or
                filename.endswith('~')):
                continue
            matches.append(os.path.join(root, filename))
    return matches


def get_sources(root):
    for dirpath in ['pysped', 'tests']:
        path = os.path.join(root, dirpath)
        for fname in list_recursively(path, '*.py'):
            if fname.endswith('__init__.py'):
                continue
            yield fname

        #yield os.path.join(root, 'setup.py')


class ClassInittableMetaType(type):
    # pylint fails to understand this is a metaclass
    def __init__(self, name, bases, namespace):
        type.__init__(self, name, bases, namespace)
        self.__class_init__(namespace)


class SourceTest(object, metaclass=ClassInittableMetaType):
    @classmethod
    def __class_init__(cls, namespace):
        root = os.path.dirname(os.path.dirname(pysped.__file__))
        cls.root = root
        for filename in get_sources(root):
            testname = filename[len(root):]
            if not cls.filename_filter(testname):
                continue
            testname = testname[:-3].replace('/', '_')
            name = 'test_%s' % (testname, )
            func = lambda self, r=root, f=filename: self.check_filename(r, f)
            func.__name__ = name
            setattr(cls, name, func)

    def check_filename(self, root, filename):
        pass

    @classmethod
    def filename_filter(cls, filename):
        if cls.__name__ == 'SourceTest':
            return False
        else:
            return True


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
