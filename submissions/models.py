import os
from django.db import models
from config.settings.common import ROOT_DIR
from hackathon.users.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import threading
import numpy as np
from sklearn import metrics


result_file = open(str(ROOT_DIR) + '/test.csv')
real_private = []
real_public = []
public_indexes = []
i = 0
for r in result_file:
	if i%10==0:  # Private (20%)
		real_public.append(int(r))
		public_indexes.append(i)
		
	else:
		real_private.append(int(r))
	i+=1


def auc(real, pred):
	real = np.array(real)
	pred = np.array(pred)
	# fpr, tpr, thresholds = metrics.roc_curve(real, pred, pos_label=1)
	# result = metrics.auc(fpr, tpr)
	result = metrics.roc_auc_score(real, pred)
	return result


class Submission(models.Model):

	submissionfile = models.FileField(upload_to='documents/')
	auc_public = models.FloatField(null=True, blank=True)
	auc_private = models.FloatField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)  

	def __unicode__(self):
		return u'%s submission: %s' % (self.user.username, self.submissionfile.url)

	def compute_score(self):
		predicted_private = []
		predicted_public = []
		results_file = open(str(ROOT_DIR) + '/hackathon' + self.submissionfile.url)
		i = 0
		for r in results_file:
			if i%10==0:
				predicted_public.append(float(r))
			else:
				predicted_private.append(float(r))
			i+=1

		self.auc_public = auc(real_public, predicted_public)
		# self.auc_private = auc(real_private, predicted_private)
		self.save()

 
@receiver(post_save, sender=Submission)
def submission_done(sender, **kwargs):
	"""
		After save compute score in a new thread
	"""
	submission = kwargs['instance']
	if submission.auc_public is None:
		print 'creating thread to compute auc...'
		score_computation_thread = threading.Thread(target=submission.compute_score,args=[])
		score_computation_thread.start()



