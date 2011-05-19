# -*- coding: utf-8 -*-

import unittest2 as unittest

from AccessControl import Unauthorized

from plone.testing import z2
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

    def testProposalWorkflowChain(self):
        """Check the whole Proposal workflow chain for a proposal
        that gets to plenary.
        """

        portal = self.layer['portal']
        wt = portal.portal_workflow

        setRoles(portal, TEST_USER_NAME, ['Manager', 'Member'])
        login(portal, TEST_USER_NAME)
        self.layer['folder'].invokeFactory('collective.libreorganizacion.proposal', 'proposal')
        proposal = self.layer['folder']['proposal']

        # It starts as a draft
        self.assertEqual(wt.getInfoFor(proposal, 'review_state'), 'draft')
        # In this state, Electors can't comment
        self.assertFalse('Reply to item' in self.getPermissions(proposal, 'Elector'))
        # and noone else can see the item
        self.assertFalse('View' in self.getPermissions(proposal, 'Anonymous'))
        # The creator can edit it, but not the rest of electors
        self.assertTrue('Modify portal content' in self.getPermissions(proposal, 'Owner'))
        self.assertFalse('Modify portal content' in self.getPermissions(proposal, 'Elector'))

        # After submitting, the proposal becomes visible
        wt.doActionFor(proposal, 'submit')
        self.assertTrue('View' in self.getPermissions(proposal, 'Anonymous'))
        # and can be supported by electors, but not by other users
        self.assertTrue('Content Ratings: User Rate' in self.getPermissions(proposal, 'Elector'))
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Reader'))
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Editor'))
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Reviewer'))
        # It's no longer editable by its owner
        self.assertFalse('Modify portal content' in self.getPermissions(proposal, 'Owner'))
        # Comments are enabled now for electors
        self.assertTrue('Reply to item' in self.getPermissions(proposal, 'Elector'))


        # Once the proposal gets enough upvotes, it is promoted to plenary.
        wt.doActionFor(proposal, 'promote')
        # In this state, supporting votes are no longer allowed
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Elector'))
        # but we can still comment
        self.assertTrue('Reply to item' in self.getPermissions(proposal, 'Elector'))


        # Voting is started! No more bla bla
        wt.doActionFor(proposal, 'start_voting')
        self.assertFalse('Reply to item' in self.getPermissions(proposal, 'Elector'))
        # nor can we support the proposal
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Elector'))
        # or edit it
        self.assertFalse('Modify portal content' in self.getPermissions(proposal, 'Owner'))
        self.assertFalse('Modify portal content' in self.getPermissions(proposal, 'Elector'))

        # but we can vote, of course
        self.assertTrue('Popoll: Vote' in self.getPermissions(proposal, 'Elector'))


        # Voting is finished! We can't vote anymore
        wt.doActionFor(proposal, 'archive')
        self.assertFalse('Popoll: Vote' in self.getPermissions(proposal, 'Elector'))
        # but the proposal remains visible
        self.assertTrue('View' in self.getPermissions(proposal, 'Anonymous'))


    def testProposalExpired(self):
        """Check the Proposal workflow chain expired state
        for a proposal that doesn't get enough support and expires.
        """

        portal = self.layer['portal']
        wt = portal.portal_workflow

        setRoles(portal, TEST_USER_NAME, ['Manager', 'Member'])
        login(portal, TEST_USER_NAME)
        self.layer['folder'].invokeFactory('collective.libreorganizacion.proposal', 'proposal')
        proposal = self.layer['folder']['proposal']

        wt.doActionFor(proposal, 'submit')
        wt.doActionFor(proposal, 'expire')

        # The proposal remains visible
        self.assertTrue('View' in self.getPermissions(proposal, 'Anonymous'))
        # But it can't be supported
        self.assertFalse('Content Ratings: User Rate' in self.getPermissions(proposal, 'Elector'))

        # And we can't discuss about it
        self.assertFalse('Reply to item' in self.getPermissions(proposal, 'Elector'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
