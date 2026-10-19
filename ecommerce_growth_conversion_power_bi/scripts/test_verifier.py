"""Regression controls for report alias scopes and floating-point page bounds."""
import unittest
from pipeline import channel
from verify_project import scoped_nodes,field_binding,within_bounds

class VerifierTests(unittest.TestCase):
    def test_deleted_source_or_medium_is_unknown_before_channel_rules(self):
        for source,medium in [('(data deleted)','referral'),('google','(data deleted)'),(' (DATA DELETED) ','organic'),('<Other>','referral'),('google','<Other>')]:
            with self.subTest(source=source,medium=medium):
                self.assertEqual(channel(source,medium),'Unknown / masked')
    def test_channel_fix_preserves_observed_and_residual_channels(self):
        for source,medium,expected in [('(direct)','(none)','Direct'),('google','organic','Organic Search'),('partner','referral','Referral'),('google','cpc','Paid Search'),('new-partner','custom','Other observed')]:
            with self.subTest(source=source,medium=medium):
                self.assertEqual(channel(source,medium),expected)

    def test_entity_reference(self):
        self.assertEqual(field_binding({'Expression':{'SourceRef':{'Entity':'DimDate'}},'Property':'date'},{}),('DimDate','date'))
    def test_alias_scope_and_missing_alias(self):
        member={'Expression':{'SourceRef':{'Source':'d'}},'Property':'channel'}
        tree=[{'From':[{'Name':'d','Entity':'DimChannel'}],'Filter':{'Column':member}}, {'Filter':{'Column':member}}]
        found=[field_binding(n['Column'],a) for n,a in scoped_nodes(tree) if 'Column' in n]
        self.assertEqual(found,[('DimChannel','channel'),(None,'channel')])
    def test_nested_alias_shadows(self):
        tree={'From':[{'Name':'d','Entity':'DimDate'}],'Query':{'From':[{'Name':'d','Entity':'DimChannel'}],'Column':{'Expression':{'SourceRef':{'Source':'d'}},'Property':'channel'}}}
        self.assertEqual([field_binding(n['Column'],a) for n,a in scoped_nodes(tree) if 'Column' in n],[('DimChannel','channel')])
    def test_rounding_does_not_mask_true_overflow(self):
        self.assertTrue(within_bounds({'x':0,'y':700,'width':100,'height':20.0000000000001},100,720))
        self.assertFalse(within_bounds({'x':0,'y':700,'width':100,'height':20.01},100,720))
        self.assertFalse(within_bounds({'x':-1,'y':0,'width':100,'height':20},100,720))

if __name__=='__main__':unittest.main()
