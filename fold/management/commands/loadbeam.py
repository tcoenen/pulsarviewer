import errno
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from fold.models import Bestprof, FoldedImage


def match_files(png_files, bestprof_files):
    tmp = {}

    for f in png_files:
        d, fn = os.path.split(f)
        k = fn[:-4]
        tmp[k] = [f]

    for f in bestprof_files:
        d, fn = os.path.split(f)
        k = fn[:-len('.pfd.bestprof')]
        if k in tmp:
            tmp[k].append(f)

    incomplete = []
    for key, value in tmp.iteritems():
        if len(value) != 2:
            incomplete.append(key)

    for k in incomplete:
        del tmp[k]
    return list(tmp.values())


class Command(BaseCommand):
    args = '<pulpsearch style output search output directory> <beam name>'
    help = 'Load all pulsar folds from search'

    def handle(self, *args, **kwargs):
        if not args or len(args) != 2:
            msg = 'Specify 1 search output dir and 1 beam name (no spaces).'
            raise CommandError(msg)

        folds_root = os.path.join(args[0], 'QUICKLOOK')
        bestprof_files = []
        png_files = []
        try:
            for root, dirs, files in os.walk(folds_root):
                for f in files:
                    if f.endswith('.pfd.bestprof'):
                        bestprof_files.append(os.path.join(root, f))
                    elif f.endswith('.png'):
                        png_files.append(os.path.join(root, f))
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise CommandError('No FOLDS directory: %s' % folds_root)
        except:
            raise

        if not bestprof_files:
            raise CommandError('No .bestprof files in %s' % folds_root)

        matched_files = match_files(png_files, bestprof_files)

        failures = []
        for f1, f2 in matched_files:
            try:
                new = Bestprof.objects.create_bestprof(f2, args[1])
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
                    failures.append('File probably already uploaded: %s' % f2)
                except:
                    print 'WHATEVER IS WRONG'
                else:
                    try:
                        new_image = FoldedImage.objects.create_image(f1,
                                                                     args[1],
                                                                     new)
                    except IOError, e:
                        if e.errno == errno.ENOENT:
                            msg = 'File does not exist: %s' % f1
                            failures.append(msg)
                    except:
                        raise
                    else:
                        new_image.save()

        if failures:
            msg = 'Problems with: \n%s' % ('\n'.join(failures))
            raise CommandError(msg)
