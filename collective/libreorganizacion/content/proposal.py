# -*- coding: utf-8 -*-

# CMF and Zope imports
from zope import schema
from zope.interface import Interface

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from collective.libreorganizacion import _


# INICIO VOCABULARIES A ELIMINAR
# Vocabularies
TOPICS = [
  ('derechoshumanos', 'Derechos Humanos'),
  ('derechosanimales', 'Derechos de los animales'),
  ('ecologia', 'Ecología y desarrollo sostenible'),
  ('etc', 'Etc.'),
    ]
SCOPES = [
  ('global', 'Global'),
  ('international', 'International'),
  ('national', 'National'),
  ('regional', 'Regional'),
  ('provincial', 'Provincial'),
  ('local', 'Local'),
]


class IProposal(Interface):
    """An entry (proposal) in a LibreOrganizacion directory
    """

    title = schema.TextLine(
        title=_(u'Slogan'),
        )

    image = NamedImage(
        title=_(u'Imagen'),
        )

    text = RichText(
        title=_(u'Texto'),
        )

    topics = schema.Choice(
        title=_(u'Temas'),
        description=_(u'Temas de la propuesta'),
        values=TOPICS,
        )

    scope = schema.Choice(
        title=_(u'Ámbito'),
        description=_(u'Ámbito territorial de la propuesta'),
        values=SCOPES,
        )

    #TODO: hacer Choice con vocabulario de países
    country = schema.TextLine(
        title=_(u'País'),
        )
