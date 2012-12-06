import errno

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from fold.models import Bestprof


class Command(BaseCommand):
    args = '<PRESTO .pfd.bestprof file> <beam name>'
    help = 'Load a single PRESTO .bestprof file.'

    def handle(self, *args, **kwargs):
        if not args or len(args) != 2:
            raise CommandError('Specify 1 and 1 beam name (no spaces)')

        try:
            new = Bestprof.objects.create_bestprof(args[0], args[1])
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise CommandError('File does not exist: %s' % args[0])
        except:
            raise
        else:
            try:
                new.save()
            except IntegrityError, e:
                raise CommandError('File probably already uploaded: %s' %
                                   args[0])
