import unittest2 as unittest

from plone.testing import z2
from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile


from zope.configuration import xmlconfig

from Products.CMFCore.utils import getToolByName


class LibreOrganizacionLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import collective.libreorganizacion
        xmlconfig.file('configure.zcml', collective.libreorganizacion,
                       context=configurationContext)
        z2.installProduct(app, 'collective.libreorganizacion')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'collective.libreorganizacion:default')


LIBREORGANIZACION_FIXTURE = LibreOrganizacionLayer()

LIBREORGANIZACION_INTEGRATION_TESTING = IntegrationTesting(bases=(LIBREORGANIZACION_FIXTURE,), name="LibreOrganizacion:Integration")
LIBREORGANIZACION_FUNCTIONAL_TESTING = FunctionalTesting(bases=(LIBREORGANIZACION_FIXTURE,), name="LibreOrganizacion:Functional")

class TestProductInstall(unittest.TestCase):
    layer = LIBREORGANIZACION_INTEGRATION_TESTING

    def testTypesInstalled(self):
        pt = getToolByName(self.layer['portal'], 'portal_types')
        self.failUnless('collective.libreorganizacion.proposal' in pt.objectIds(),
                            'proposal content type not installed')

    def testOnlyManagerCanAddKeywords(self):
        sp = self.layer['portal'].portal_properties.site_properties
        self.failUnlessEqual(sp.getProperty('allowRolesToAddKeywords'), ('Manager',))

    def testCustomTopicView(self):
        "Test that the collection type have an extra custom view method."
        pt = getToolByName(self.layer['portal'], 'portal_types')
        topic_type = pt.Topic
        self.failUnless('custom_folder_summary_view' in \
                        topic_type.getProperty('view_methods'))


    def testElectorRole(self):
        """Comprobar que existe el rol 'Elector'"""
        self.assertTrue('Elector' in self.layer['portal'].valid_roles())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
