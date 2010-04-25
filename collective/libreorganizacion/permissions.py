
# CMF and Archetypes imports
from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes

# Product imports
from config import PROJECTNAME

# Being generic by defining an "Add" permission
# for each content type in the product
ADD_CONTENT_PERMISSIONS = {}
types = listTypes(PROJECTNAME)
for atype in  types:
    permission = "%s: Add %s" % (PROJECTNAME, atype['portal_type'])
    ADD_CONTENT_PERMISSIONS[atype['portal_type']] = permission
