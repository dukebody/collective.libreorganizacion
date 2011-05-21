# -*- coding: utf-8 -*-

import unittest2 as unittest
import doctest

from AccessControl import Unauthorized

from plone.testing import z2
from plone.testing import layered
from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile

from plone.app.testing import setRoles
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME

from plone.app.workflow.interfaces import ISharingPageRole

from zope.configuration import xmlconfig
from zope.component import getUtilitiesFor

from Products.CMFCore.utils import getToolByName


class LibreOrganizacionLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import collective.libreorganizacion
        xmlconfig.file('configure.zcml', collective.libreorganizacion,
                       context=configurationContext)
        z2.installProduct(app, 'Products.PlonePopoll')
        z2.installProduct(app, 'collective.libreorganizacion')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'collective.libreorganizacion:default')

        setRoles(portal, TEST_USER_NAME, ['Manager', 'Member'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder1')
        folder = portal.folder1
        setRoles(portal, TEST_USER_NAME, ['Member'])

        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser('elector', 'elector', ['Member'], [])
        folder.manage_setLocalRoles('elector', ['Member', 'Contributor', 'Elector'])
        self['folder'] = folder


LIBREORGANIZACION_FIXTURE = LibreOrganizacionLayer()

LIBREORGANIZACION_INTEGRATION_TESTING = IntegrationTesting(bases=(LIBREORGANIZACION_FIXTURE,), name="LibreOrganizacion:Integration")
LIBREORGANIZACION_FUNCTIONAL_TESTING = FunctionalTesting(bases=(LIBREORGANIZACION_FIXTURE,), name="LibreOrganizacion:Functional")


class TestProductInstall(unittest.TestCase):
    layer = LIBREORGANIZACION_INTEGRATION_TESTING

    def getPermissions(self, obj, role):
        return [p['name'] for p in obj.permissionsOfRole(role) if p['selected']]

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

    def testProposalWorkflow(self):
        """Comprobar que el tipo Propuesta está asociado al
        workflow correspondiente."""
        portal = self.layer['portal']
        wt = portal.portal_workflow
        self.failUnless('collective.libreorganizacion.proposal_workflow' in wt.getChainForPortalType('collective.libreorganizacion.proposal'))

    def testElectorInSharing(self):
        """Comprobar que se puede asignar el rol Elector desde la
        pestaña 'Compartir'."""
        roles = dict(getUtilitiesFor(ISharingPageRole))
        self.assertTrue('Elector' in roles)

    def testElectorCanCreateProposals(self):
        """Comprobar que un Elector puede crear propuestas"""
        portal = self.layer['portal']
        login(portal, 'elector')
        self.layer['folder'].invokeFactory('collective.libreorganizacion.proposal', 'proposal1')

    def testNonElectorsCantCreateProposals(self):
        """Comprobar que un no Elector NO puede crear propuestas"""
        # el usuario por defecto sólo es miembro, pero no elector
        self.assertRaises(Unauthorized,
            self.layer['folder'].invokeFactory, 'collective.libreorganizacion.proposal', 'proposal1')

    def testElectorsCanCommentOnProposals(self):
        """Comprobar que un Elector puede comentar las propuestas"""
        portal = self.layer['portal']
        self.assertTrue('Reply to item' in self.getPermissions(portal, 'Elector'))

    def testNonElectorsCantCommentOnProposals(self):
        """Comprobar que un no Elector NO puede comentar las propuestas"""
        portal = self.layer['portal']
        self.assertFalse('Reply to item' in self.getPermissions(portal, 'Member'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    suite.addTest(layered(doctest.DocFileSuite('test_workflow.txt'), LIBREORGANIZACION_INTEGRATION_TESTING))
    return suite
