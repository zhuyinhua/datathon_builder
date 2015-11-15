# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Max, Count
from config.settings.common import ROOT_DIR

from hackathon.users.models import User
from .models import Submission, auc
from .forms import SubmissionForm

result_file = open(str(ROOT_DIR) + '/test.csv')
real_public = []
i = 0
for r in result_file:
	if i%20==0:  # Private (20%)
		real_public.append(int(r))
	i+=1


@login_required
def submissions_list(request):
	current_user = request.user

	# Handle file upload
	if request.method == 'POST':
		form = SubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			
			try:
			# predicted_public = []
				predicted_public = [0.0]*17084
				i = j = 0
				for r in request.FILES['submissionfile']:
					if r=='':
						continue
					if i%20==0:
						predicted_public[j] = float(r)
						j+=1
						# predicted_public.append(float(r))
					i+=1
				auc_public = auc(real_public, predicted_public)
				newdoc = Submission(submissionfile=request.FILES['submissionfile'], user=current_user, auc_public=auc_public)
				newdoc.save()
			except:
				pass

			# Redirect to the document list after POST
			return HttpResponseRedirect(reverse('list'))
	else:
		form = SubmissionForm()  # A empty, unbound form

    # Load documents for the list page
	documents = Submission.objects.filter(user=current_user).order_by('-created_at')
	
    # Render list page with the documents and the form
	return render_to_response(
		'submissions/list.html',
		{'submissions': documents, 'form': form},
		context_instance=RequestContext(request)
	)


def leaderboard(request):

	teams = Submission.objects.exclude(auc_public__isnull=True).values('user').annotate(auc=Max('auc_public'), last_update=Max('created_at'), number=Count('submissionfile')).order_by('-auc')
	for team in teams:
		team['user'] = User.objects.get(pk=team['user'])
		team['user'].name

	return render_to_response(
		'submissions/leaderboard.html',
		{'teams': teams},
		context_instance=RequestContext(request)
	)


def leaderboard_final(request):

	teams = Submission.objects.exclude(auc_private__isnull=False).order_by('-auc')
	for team in teams:
		team['user'] = User.objects.get(pk=team['user'])
		team['user'].name

	return render_to_response(
		'submissions/leaderboard.html',
		{'teams': teams},
		context_instance=RequestContext(request)
