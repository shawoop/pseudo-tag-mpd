PLUGIN_NAME = "Pseudo-tag MPD"
PLUGIN_AUTHOR = "/dev/null"
PLUGIN_DESCRIPTION = "Update metadata (tags) in an mpd database without modifying the source audio file."
PLUGIN_VERSION = '0.0.1'
PLUGIN_API_VERSIONS = [ "2.0", "2.1", "2.2"]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"

from os.path import basename

from picard.album import Album
from picard.ui.itemviews import BaseAction, register_album_action

from .mpd import Database, Directory, Song

INPUT_DB = "/home/MYUSER/.config/mpd/database"
OUTPUT_DB = "/home/MYUSER/.config/mpd/database_out"

db = Database(INPUT_DB)

class SaveToMPDDatabase(BaseAction):
    NAME = 'Save to MPD database'

    @staticmethod
    def append_tag(tags, tag, value):
        if tag not in tags:
            tags[tag] = list()
        tags[tag].append(value)
        return tags

    def callback(self, objs):
        for album in objs:
            if isinstance(album, Album) and album.loaded == True:
                directory_found = False
                for directory in db.directories:
                    for song in directory.songs:
                        if song.name == basename(album.tracks[0].linked_files[0].filename):
                            directory_found = True
                            break
                    if directory_found:
                        break
                for track in album.tracks:
                    tags = {}
                    for name, value in track.metadata.items():
                        if name == "artist":
                            SaveToMPDDatabase.append_tag(tags, "Artist", value)
                        if name == "artistsort":
                            SaveToMPDDatabase.append_tag(tags, "ArtistSort", value)
                        if name == "album":
                            SaveToMPDDatabase.append_tag(tags, "Album", value)
                        if name == "albumartist":
                            SaveToMPDDatabase.append_tag(tags, "AlbumArtist", value)
                        if name == "albumartistsort":
                            SaveToMPDDatabase.append_tag(tags, "AlbumArtistSort", value)
                        if name == "title":
                            SaveToMPDDatabase.append_tag(tags, "Title", value)
                        if name == "tracknumber":
                            SaveToMPDDatabase.append_tag(tags, "Track", value)
                        if name == "date":
                            SaveToMPDDatabase.append_tag(tags, "Date", value)
                        if name == "originaldate":
                            SaveToMPDDatabase.append_tag(tags, "OriginalDate", value)
                        if name == "discnumber":
                            SaveToMPDDatabase.append_tag(tags, "Disc", value)
                        if name == "label":
                            SaveToMPDDatabase.append_tag(tags, "Label", value)
                        # if name.startswith("musicbrainz"):
                        #     SaveToMPDDatabase.append_tag(tags, name.upper(), value)
                    if directory_found:
                        song_found = False
                        for song in directory.songs:
                            for linked_file in track.linked_files:
                                if basename(linked_file.filename) == song.name:
                                    song_found = True
                                    break
                            if song_found:
                                for key in tags:
                                    song.tags[key] = tags[key]
                                break
                    else:
                        pass
                        # directory = Directory()
                        # db.directories.append(directory)

        db.write(OUTPUT_DB)
                        
register_album_action(SaveToMPDDatabase())
