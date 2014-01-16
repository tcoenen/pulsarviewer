import errno
import os
import math

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from fold.models import Bestprof, FoldedImage

from fold import coords


class Command(BaseCommand):
    args = '<pulpsearch style output search output directory> <beam name> <ra> <dec>'
    help = 'Load all pulsar folds from search'

    def handle(self, *args, **kwargs):
        if not args or len(args) != 4:
            msg = 'Specify search output dir, beam (no spaces), RA and DEC.'
            raise CommandError(msg)

        beam_name = args[1]

        ra = coords.RightAscension.from_sexagesimal(args[2])
        dec = coords.Declination.from_sexagesimal(args[3])
        ra_deg = 180 * ra.to_radians() / math.pi
        dec_deg = 180 * dec.to_radians() / math.pi
        self.stdout.write('(RA, DEC) = (%.2f, %.2f)' % (ra_deg, dec_deg))

        # find relevant files
        in_dir = os.path.realpath(args[0])
        bestprof_files = set()
        png_files = set()

        files = os.listdir(in_dir)
        for f in files:
            if f.endswith('.pfd.bestprof'):
                bestprof_files.add(f[:-13])
            elif f.endswith('.png'):
                png_files.add(f[:-4])

        basenames = bestprof_files.intersection(png_files)

        if not basenames:
            raise CommandError('No folds found in: %s' % in_dir)

        failures = []
        for bn in basenames:
            bestprof_file = os.path.join(in_dir, bn + '.pfd.bestprof')
            png_file = os.path.join(in_dir, bn + '.png')

            assert os.path.exists(bestprof_file)
            assert os.path.exists(png_file)

            try:
                new = Bestprof.objects.create_bestprof(
                    bestprof_file, beam_name, ra_deg, dec_deg, ra, dec
                )
            except IOError, e:
                if e.errno == errno.ENOENT:
                    msg = 'File does not exist: %s' % bestprof_file
                    failures.append(msg)
            except:
                raise
            else:
                try:
                    new.save()
                except IntegrityError:
                    msg = 'File probably already uploaded: %s' % bestprof_file
                    failures.append(msg)
                except Exception, e:
                    print e
                    msg = 'Unknown exception, skipping: %s' % bestprof_file
                    failures.append(msg)
                else:
                    try:
                        new_image = FoldedImage.objects.create_image(
                            png_file, beam_name, new
                        )
                    except IOError, e:
                        if e.errno == errno.ENOENT:
                            msg = 'File does not exist: %s' % png_file
                            failures.append(msg)
                    except:
                        # Database in messy state, should read up on database
                        # transactions and/or provide a clean-up command.
                        # (Because .bestprof was loaded but not the .png)
                        raise
                    else:
                        new_image.save()

        if failures:
            msg = 'Problems with: \n%s' % ('\n'.join(failures))
            raise CommandError(msg)
