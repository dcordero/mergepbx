from .core import DictionaryBoundObject
from . import isa

class PBXProjFile(DictionaryBoundObject):
    MAPPED_ATTRIBUTES = ("archiveVersion", "objectVersion", "rootObject")
    def __init__(self, plist, ignore_unknown_objects=False):
        super(self.__class__, self).__init__(plist, self.__class__.MAPPED_ATTRIBUTES)
        self._plist = plist
        self._classes = PBXClasses(self._plist["classes"])
        self._objects = PBXObjects(self._plist["objects"], ignore_unknown_objects)
        self._load_phases()

    def _load_phases(self):
        self._phases = dict()
        phases = (
            ("Frameworks", "PBXFrameworksBuildPhase"),
            ("Sources", "PBXSourcesBuildPhase"),
            ("Resources", "PBXResourcesBuildPhase")
        )

        for (section, phase_isa) in phases:
            phase_object_files = self._objects.getfiles(phase_isa)
            if not phase_object_files is None:
                self._phases[section] = set(phase_object_files)

    def get_objects(self):
        return self._objects

    def phase_of_object(self, identifier):
        for phase, files in self._phases.iteritems():
            if identifier in files:
                return phase

class PBXClasses(object):
    def __init__(self, data_dict):
        self.data_dict = data_dict

class PBXObjects(object):
    def __init__(self, data_dict, ignore_unknown_objects):
        self.data_dict = data_dict
        self.ignore_unknown_objects = ignore_unknown_objects

    def keys(self):
        return self.data_dict.keys()

    def get(self, key):
        return self._make_isa_object(key, self.data_dict[key])

    def iterobjects(self, isa=None):
        if self.ignore_unknown_objects:
            items_iter = ((key, value) for key,value in self.data_dict.iteritems() if isa.is_known(value["isa"]))
        else:
            items_iter = self.data_dict.iteritems()

        return (
            (key, self._make_isa_object(key, value)) for key, value in items_iter \
            if isa == None or value["isa"] == isa
        )

    def getobjects(self, isa=None):
        return tuple(self.iterobjects(isa))

    def getfiles(self,isa):
        found_objects = self.getobjects(isa)
        if len(found_objects) > 0:
	    objectFiles = list ();
	    for isaElement in self.getobjects(isa):
	        objectFiles.extend (isaElement[1].files)
            return objectFiles
        else:
            return None

    def _make_isa_object(self, identifier, isa_dict):
        return isa.create(identifier, isa_dict)
