from inventory.tests.test_migrations import TestMigrations
from inventory.tests.factories import StyleValueFactory
from inventory.models import StyleValue


class TestBaselineStyles(TestMigrations):

    migrate_from = '0005_auto_20201221_1913'
    migrate_to = '0004_auto_20201221_1909'

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
