# CMF and Zope imports
from Products.CMFCore import permissions
from zope.interface import implements

# Archetypes imports
from Products.Archetypes import atapi
from Products.Archetypes.atapi import DisplayList

# Widgets imports
from Products.ATCountryWidget.Widget import CountryWidget

# Product imports
from collective.libreorganizacion.config import PROJECTNAME
from collective.libreorganizacion.interfaces import ILibreOrganizacion

# INICIO VOCABULARIES A ELIMINAR
# Vocabularies
TOPICS = DisplayList((
  ('derechoshumanos', 'Derechos Humanos'),
  ('derechosanimales', 'Derechos de los animales'),
  ('ecologia', 'Ecología y desarrollo sostenible'),
  ('etc', 'Etc.'),
))
SCOPE = DisplayList((
  ('global', 'Global'),
  ('international', 'International'),
  ('national', 'National'),
  ('regional', 'Regional'),
  ('provincial', 'Provincial'),
  ('local', 'Local'),
))
# FIN EJEMPLO A ELIMINAR


# Schema definition
LibreOrganizacionSchema = atapi.BaseSchema.copy() +  atapi.Schema((

    atapi.TextField('slogan',
              searchable = 1,
              required = 1,
              storage = atapi.AttributeStorage(),
              widget=atapi.TextAreaWidget(
              		description="Slogan",
              		label="Slogan"),
              ),
    atapi.ImageField('image',
              max_size = (768,768),
              languageIndependent = True,
              storage = atapi.AttributeStorage(),
              sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },        
              ),            
    atapi.TextField('text',
              searchable = 1,
              required = 1,
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/plain',
                                       'text/structured',
                                       'text/html',),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
              		label = 'Text'),       
              ),
    # INICIO VOCABULARIES A ELIMINAR
    atapi.StringField('topics',
              searchable = 1,
              required = 1,
              vocabulary=TOPICS,
              widget=atapi.SelectionWidget(format='select', 
                  label='Topics',
                  label_msgid='label_topics',
              		description='Topics of the proposal',
              		description_msgid='help_topics',
                  i18n_domain='libreorganizacion'),
              ),
    atapi.StringField('scope',
              searchable = 1,
              required = 1,
              vocabulary=SCOPE,
              widget=atapi.SelectionWidget(format='select', 
                  label='Scope',
                  label_msgid='label_scope',
              		description='Territorial scope of the proposal',
              		description_msgid='help_scope',
                  i18n_domain='libreorganizacion'),
              ),
    # FIN VOCABULARIES A ELIMINAR
    # INICIO AT COUNTRY WIDGET
    atapi.StringField('country',
    			widget=CountryWidget(
    					label='Country',
              		label_msgid='label_country',
                      provideNullValue=1,      # this is default
                      nullValueTitle='-',      # this is default
                      description='Select an country',
                      description_msgid='help_country',
                      i18n_domain='libreorganizacion')
    ),
    # FIN AT COUNTRY WIDGET
    ))


class LibreOrganizacion(atapi.BaseContent):
    """An Archetype for an LibreOrganizacion application
    """
    implements(ILibreOrganizacion)

    schema = LibreOrganizacionSchema
    
    _at_rename_after_creation = True  # ??? isn't this the default?
    
    def tag(self, **kwargs):
        return self.getField('image').tag(self, **kwargs)

atapi.registerType(LibreOrganizacion, PROJECTNAME)
