from django.conf.urls import patterns, url
from views import BestprofListView, CandidatePHistogramView, ConstraintsView
from views import BestprofDetailView, CandidatePDMView, CandidatePChiView

urlpatterns = patterns('',
    url(r'(?P<pk>\d+)/', BestprofDetailView.as_view(), name='bestprof_detail'),
    url(r'pdm/', CandidatePDMView.as_view(), name='candidate_pdm_graph'),
    url(r'pchi/', CandidatePChiView.as_view(), name='candidate_pchi_graph'),
    url(r'phist/', CandidatePHistogramView.as_view(),
        name='candidate_p_histogram'),
    url(r'constraints/', ConstraintsView.as_view(),
        name='candidate_constraints'),
    url(r'', BestprofListView.as_view(), name='bestprof_list'),
)
