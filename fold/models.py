import os

from django.db import models
from django.core.files import File
import bestprof


class BestprofManager(models.Manager):
    def create_bestprof(self, filename, beamname):
        bpf = bestprof.BestprofFile(filename)
        with open(filename) as f:
            file_hash = hash(f.read())

        new = Bestprof(
            file_hash=file_hash,
            beam=beamname,
            file=File(open(filename)),
            input_file=bpf.header.input_file,
            candidate=bpf.header.candidate,
            telescope=bpf.header.telescope,
            epoch_topo=bpf.header.epoch_topo,
            epoch_bary_mjd=bpf.header.epoch_bary_mjd,
            t_sample=bpf.header.t_sample,
            data_folded=bpf.header.data_folded,
            data_avg=bpf.header.data_avg,
            data_stddev=bpf.header.data_stddev,
            profile_bins=bpf.header.profile_bins,
            profile_avg=bpf.header.profile_avg,
            profile_stddev=bpf.header.profile_stddev,
            reduced_chi_sq=bpf.header.reduced_chi_sq,
            best_dm=bpf.header.best_dm,
            p_topo=bpf.header.p_topo[0],
            p_dot_topo=bpf.header.p_dot_topo[0],
            p_dot_dot_topo=bpf.header.p_dot_dot_topo[0],
            p_bary=bpf.header.p_bary[0],
            p_dot_bary=bpf.header.p_dot_bary[0],
            p_dot_dot_bary=bpf.header.p_dot_dot_bary[0],
        )
        return new


def generate_bestprof_filename(instance, filename):
    return 'fold/%s/%s' % (instance.beam, os.path.basename(filename))


class Bestprof(models.Model):
    '''
    Header of bestprof file.
    '''
    file_hash = models.IntegerField(unique=True, editable=False)
    beam = models.CharField(max_length=255)
    file = models.FileField(upload_to=generate_bestprof_filename,
                            editable=False)

    input_file = models.CharField(max_length=255)
    candidate = models.CharField(max_length=255)
    telescope = models.CharField(max_length=255)
    epoch_topo = models.FloatField()
    epoch_bary_mjd = models.FloatField()
    t_sample = models.FloatField()
    data_folded = models.IntegerField()
    data_avg = models.FloatField()
    data_stddev = models.FloatField()
    profile_bins = models.IntegerField()
    profile_avg = models.FloatField()
    profile_stddev = models.FloatField()
    reduced_chi_sq = models.FloatField()
    best_dm = models.FloatField()
    p_topo = models.FloatField()
    p_dot_topo = models.FloatField()
    p_dot_dot_topo = models.FloatField()
    p_bary = models.FloatField()
    p_dot_bary = models.FloatField()
    p_dot_dot_bary = models.FloatField()

    objects = BestprofManager()

    def __unicode__(self):
        return 'DM = %.3f P = %.4f (ms)' % (self.best_dm, self.p_bary)
