# -*- coding: utf-8 -*-

# CMF and Zope imports
from zope import schema
from zope.interface import Interface

from collective.libreorganizacion import _


class IPoll(Interface):
    """A poll to vote at. It will contain two or more options to vote for.
    """

    title = schema.TextLine(
        title=_(u'Title'),
        )
