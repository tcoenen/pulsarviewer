from django.views.generic import ListView, DetailView
from django.http import Http404, QueryDict


from models import Bestprof, FoldedImage

OK_GET_PARAMETERS = set([
    'lo_dm',
    'hi_dm',
    'lo_p',
    'hi_p',
    'lo_redchisq',
    'hi_redchisq',
    'beam',
    'order',
])


def check_parameters(get_pars):
    qd = get_pars.copy()
    for k in get_pars:
        if not k in OK_GET_PARAMETERS:
            del qd[k]
    return qd


class BestprofListView(ListView):
    model = Bestprof
    paginate_by = 50

    def get_queryset(self):
        return Bestprof.objects.with_constraints(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super(BestprofListView, self).get_context_data(**kwargs)
        context['selection'] = check_parameters(self.request.GET).urlencode()
        return context


class BestprofDetailView(DetailView):
    model = Bestprof

    def get_context_data(self, **kwargs):
        context = super(BestprofDetailView, self).get_context_data(**kwargs)

        img = FoldedImage.objects.get(bestprof=context['object'].pk)

        context['selection'] = check_parameters(self.request.GET).urlencode()
        context['img'] = img
        context['dm'] = '%.2f' % context['object'].best_dm
        context['p0'] = '%.2f' % context['object'].p_bary
        context['redchisq'] = '%.3f' % context['object'].reduced_chi_sq
        return context


class CandidatePDMView(BestprofListView):
    paginate_by = 2000

    def get_template_names(self):
        # TODO: see whether this can be done less hacky
        return ['fold/pdm_graph.html']


class CandidatePChiView(BestprofListView):
    paginate_by = 2000

    def get_template_names(self):
        # TODO: see whether this can be done less hacky
        return ['fold/pchi_graph.html']


class CandidatePHistogramView(BestprofListView):
    paginate_by = None

    def get_template_names(self):
        # TODO: see whether this can be done less hacky
        return ['fold/p_hist.html']
