from tests.gbe.test_migrations import TestMigrations
from tests.factories.gbe_factories import StyleValueFactory
from gbe.models import StyleValue


class TestBaselineStyles(TestMigrations):

    migrate_from = '0004_auto_20201224_1145'
    migrate_to = '0003_auto_20201224_0729'

    def setUpBeforeMigration(self, apps):
        self.value = StyleValueFactory(
            style_version__currently_live=True,
            style_version__currently_test=True)

    def test_tags_migrated(self):
        values = StyleValue.objects.filter(
            style_property=self.value.style_property,
            style_version=self.value.style_version)

        self.assertEqual(values.count(), 1)
        self.assertEqual(values[0].value, self.value.value)
