from base import LibreOrganizacionTestCase
from Products.CMFCore.utils import getToolByName

class TestProductInstall(LibreOrganizacionTestCase):

    def afterSetUp(self):
        self.types = ('LibreOrganizacion',)

    def testTypesInstalled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)
                                    
    def testPortalFactoryEnabled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_factory.getFactoryTypes().keys(),
                            '%s content type not installed' % t)

    def testOnlyManagerCanAddKeywords(self):
        sp = self.portal.portal_properties.site_properties
        self.failUnlessEqual(sp.getProperty('allowRolesToAddKeywords'), ('Manager',))

    def testCustomTopicView(self):
        "Test that the collection type have an extra custom view method."
        pt = getToolByName(self.portal, 'portal_types')
        topic_type = pt.Topic
        self.failUnless('custom_folder_summary_view' in \
                        topic_type.getProperty('view_methods'))
                    
class TestInstantiation(LibreOrganizacionTestCase):
    
    def testCreateLibreOrganizacion(self):
        self.folder.invokeFactory('LibreOrganizacion', 'im1')
        self.failUnless('im1' in self.folder.objectIds())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    suite.addTest(makeSuite(TestInstantiation))
    return suite
