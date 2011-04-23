# There are too many imports here but we need pyflakes to check which ones
# are not needed easily

import time

from persistent import Persistent

from plone.registry.interfaces import IRegistry

from zope.interface import implements, implementer
from zope.component import adapts, adapter, queryUtility

from zope.annotation.interfaces import IAnnotations, IAnnotatable

from zope.event import notify

from Acquisition import aq_base, aq_inner, aq_parent
from Acquisition import Explicit

from OFS.Traversable import Traversable

from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from Products.CMFPlone.interfaces import IPloneSiteRoot, INonStructuralFolder

from zope.container.contained import ContainerModifiedEvent

from zope.lifecycleevent import ObjectCreatedEvent

try:
    # Plone 4
    from zope.lifecycleevent import ObjectAddedEvent
    from zope.lifecycleevent import ObjectRemovedEvent
except ImportError: # pragma: no cover
    # Plone 3.x
    from zope.app.container.contained import ObjectAddedEvent # pragma: no cover
    from zope.app.container.contained import ObjectRemovedEvent # pragma: no cover

from BTrees.OIBTree import OIBTree

try:
    # These exist in new versions, but not in the one that comes with Zope 2.10.
    from BTrees.LOBTree import LOBTree
    from BTrees.LLBTree import LLSet
except ImportError: # pragma: no cover
    from BTrees.OOBTree import OOBTree as LOBTree # pragma: no cover
    from BTrees.OOBTree import OOSet as LLSet # pragma: no cover

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.comment import Comment

ANNOTATION_KEY = 'plone.app.discussion:conversation'


def enabled(self):
    # Returns True if discussion is enabled on the conversation

    # Fetch discussion registry
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)

    # Check if discussion is allowed globally
    if not settings.globally_enabled:
        return False

    parent = aq_inner(self.__parent__)

    def traverse_parents(obj):
        # Run through the aq_chain of obj and check if discussion is
        # enabled in a parent folder.
        for obj in self.aq_chain:
            if not IPloneSiteRoot.providedBy(obj):
                if IFolderish.providedBy(obj):
                    flag = getattr(obj, 'allow_discussion', None)
                    if flag is not None:
                        return flag
        return None

    obj = aq_parent(self)

    # If discussion is disabled for the object, bail out
    obj_flag = getattr(aq_base(obj), 'allow_discussion', None)
    if obj_flag is False:
        return False

    # Check if traversal returned a folder with discussion_allowed set
    # to True or False.
    folder_allow_discussion = traverse_parents(obj)

    if folder_allow_discussion is True:
        if not getattr(self, 'allow_discussion', None):
            return True
    elif folder_allow_discussion is False:
        if obj_flag:
            return True

    # Check if discussion is allowed on the content type
    portal_types = getToolByName(self, 'portal_types')
    document_fti = getattr(portal_types, obj.portal_type)
    if not document_fti.getProperty('allow_discussion'):
        # If discussion is not allowed on the content type,
        # check if 'allow discussion' is overridden on the content object.
        if not obj_flag:
            return False

    return True
