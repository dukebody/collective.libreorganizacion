from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

# Product imports
from config import PROJECTNAME, SKINS_DIR, GLOBALS
# Import the content types modules
from content import *
# Import the content types permissions
from permissions import ADD_CONTENT_PERMISSIONS

registerDirectory(SKINS_DIR, GLOBALS)


def initialize(context):
    
    content_types, constructors, ftis = process_types(
             listTypes(PROJECTNAME), 
             PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.portal_type)
        utils.ContentInit(kind,            
                          content_types      = (atype,),
                          permission         = ADD_CONTENT_PERMISSIONS[atype.portal_type],
                          extra_constructors = (constructor,),            
                          fti                = ftis,
                          ).initialize(context)
