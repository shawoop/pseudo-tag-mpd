import gzip
import re
from collections import OrderedDict
import os


ENCODING = "ISO-8859-1"

class Playlist:

    def __init__(self, name, fp=None):
        self.name = name
        if fp:
            self.read_playlist(fp)
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def mtime(self):
        return self.__mtime

    @mtime.setter
    def mtime(self, mtime):
        self.__mtime = mtime

    def read_playlist(self, fp):
        while True:
            line = Database.readline(fp)
            if line.startswith("mtime: "):
                self.mtime = line[7:]
            if line == "playlist_end":
                break

    def write(self, fp):
        fp.write("playlist_begin: {}\n".format(self.name).encode(ENCODING))
        fp.write("mtime: {}\n".format(self.mtime).encode(ENCODING))
        fp.write("playlist_end\n".encode(ENCODING))

class Song:
    
    def __init__(self, name, fp=None):
        self.name = name
        self.tags = OrderedDict()
        if fp:
            self.read_song(fp)
        
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def mtime(self):
        return self.__mtime

    @mtime.setter
    def mtime(self, mtime):
        self.__mtime = mtime

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, tags):
        self.__tags = tags

    def read_song(self, fp):
        while True:
            line = Database.readline(fp)
            if line.startswith("mtime: "):
                self.mtime = line[7:]
            if line[0].isupper():
                m = re.match("([A-Za-z_]+): (.*)", line)
                if not m.groups()[0] in self.tags:
                    self.tags[m.groups()[0]] = list()
                self.tags[m.groups()[0]].append(m.groups()[1])
            if line == "song_end":
                break

    def write(self, fp):
        fp.write("song_begin: {}\n".format(self.name).encode(ENCODING))
        for key in self.tags:
            for value in self.tags[key]:
                fp.write("{}: {}\n".format(key, value).encode(ENCODING))
        fp.write("mtime: {}\n".format(self.mtime).encode(ENCODING))
        fp.write("song_end\n".encode(ENCODING))


class Directory:
    
    def __init__(self, name, fp=None):
        self.name = name
        self.songs = []
        self.playlists = []
        self.directories = []
        if fp:
            self.read_directory(fp)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def mtime(self):
        return self.__mtime

    @mtime.setter
    def mtime(self, mtime):
        self.__mtime = mtime

    @property
    def directories(self):
        return self.__directories

    @directories.setter
    def directories(self, directories):
        self.__directories = directories

    @property
    def songs(self):
        return self.__songs

    @songs.setter
    def songs(self, songs):
        self.__songs = songs

    @property
    def playlists(self):
        return self.__playlists

    @playlists.setter
    def playlists(self, playlists):
        self.__playlists = playlists

    def read_directory(self, fp):
        while True:
            line = Database.readline(fp)
            if line.startswith("mtime: "):
                self.mtime = line[7:]
            # if line.startswith("begin: "):
                # self.name = line[7:]
            if line.startswith("directory: "):
                name = line[11:]
                self.directories.append(Directory(name, fp))
            if line.startswith("song_begin: "):
                name = line[12:]
                self.songs.append(Song(name, fp))
            if line.startswith("playlist_begin: "):
                name = line[16:]
                self.playlists.append(Playlist(name, fp))
            if line.startswith("end: "):
                break

    def write(self, fp, parent=[]):
        fp.write("directory: {}\n".format(self.name).encode(ENCODING))
        fp.write("mtime: {}\n".format(self.mtime).encode(ENCODING))
        name = os.path.join(*parent, self.name)
        fp.write("begin: {}\n".format(name).encode(ENCODING))
        for directory in self.directories:
            p = parent + [self.name]
            directory.write(fp, parent=p)
        for song in self.songs:
            song.write(fp)
        for playlist in self.playlists:
            playlist.write(fp)
        fp.write("end: {}\n".format(name).encode(ENCODING))


class Database:

    def __init__(self, location):
        self.location = location
        self.directories = []
        self.read()

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        self.__location = location

    @property
    def info(self):
        return self.__info

    @info.setter
    def info(self, info):
        self.__info = info

    @property
    def directories(self):
        return self.__directories

    @directories.setter
    def directories(self, directories):
        self.__directories = directories

    @staticmethod
    def readline(fp):
        return next(fp).decode("ISO-8859-1").rstrip("\n")

    def read_info(self, fp):
        info = []
        while True:
            line = self.readline(fp)
            if line == "info_end":
                break
            info.append(line)
        self.info = info

    def read(self):
        with gzip.open(self.location, "r") as fp:
            while True:
                try:
                    line = Database.readline(fp)
                    if line == "info_begin":
                        self.read_info(fp)
                    if line.startswith("directory: "):
                        name = line[11:]
                        self.directories.append(Directory(name, fp))
                except StopIteration:
                    break

    def write(self, filename):
        with gzip.open(filename, "w") as fp:
            fp.write("info_begin\n".encode(ENCODING))
            for l in self.info:
                s = l + "\n"
                fp.write(s.encode(ENCODING))
            fp.write("info_end\n".encode(ENCODING))
            for directory in self.directories:
                directory.write(fp)
