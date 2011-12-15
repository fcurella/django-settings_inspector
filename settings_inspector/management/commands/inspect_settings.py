from settings_inspector.parser import Setting
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle(self, *args, **options):
        root_setting = Setting('django.conf')
        import ipdb; ipdb.set_trace()
