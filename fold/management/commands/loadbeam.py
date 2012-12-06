import errno
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from fold.models import Bestprof


class Command(BaseCommand):
    args = '<pulpsearch style output search output directory> <beam name>'
    help = 'Load all pulsar folds from search'

    def handle(self, *args, **kwargs):
        if not args or len(args) != 2:
            msg = 'Specify 1 search output dir and 1 beam name (no spaces).'
            raise CommandError(msg)

        folds_root = os.path.join(args[0], 'QUICKLOOK')
        bestprof_files = []
        try:
            for root, dirs, files in os.walk(folds_root):
                for f in files:
                    if f.endswith('.pfd.bestprof'):
                        bestprof_files.append(os.path.join(root, f))
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise CommandError('No FOLDS directory: %s' % folds_root)
        except:
            raise

        if not bestprof_files:
            raise CommandError('No .bestprof files in %s' % folds_root)

        failures = []
        for f in bestprof_files:
            try:
                new = Bestprof.objects.create_bestprof(f, args[1])
            except IOError, e:
                if e.errno == errno.ENOENT:
                    msg = 'File does not exist: %s' % f
                    failures.append(msg)
            except:
                raise
            else:
                try:
                    new.save()
                except IntegrityError, e:
                    failures.append('File probably already uploaded: %s' % f)

        if failures:
            msg = 'Problems with: \n%s' % ('\n'.join(failures))
            raise CommandError(msg)
