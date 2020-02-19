# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-04 14:34


from __future__ import absolute_import, print_function, unicode_literals

import sys

from tqdm import tqdm

from django.db import migrations

def assigned_time(model, request):
    e = model.objects.filter(doc=request.doc, type="assigned_review_request", review_request=request).order_by('-time', '-id').first()
    return e.time if e and e.time else None

def done_time(model, request):
    if request.unused_review and request.unused_review.time:
        return request.unused_review.time
    e = model.objects.filter(doc=request.doc, type="closed_review_request", review_request=request).order_by('-time', '-id').first()
    time = e.time if e and e.time else None
    return time if time else request.time

def map_request_state_to_assignment_state(req_state_id):
    if req_state_id == 'requested':
        return 'assigned'
    elif req_state_id in ('no-review-document', 'no-review-version'):
        return 'withdrawn'
    else:
        return req_state_id

def forward(apps, schema_editor):
    ReviewRequest = apps.get_model('review', 'ReviewRequest')
    ReviewAssignment = apps.get_model('review', 'ReviewAssignment')
    Document = apps.get_model('doc', 'Document')
    ReviewRequestDocEvent = apps.get_model('doc','ReviewRequestDocEvent')
    ReviewAssignmentDocEvent = apps.get_model('doc','ReviewAssignmentDocEvent')

    sys.stderr.write('\n') # introduce a newline before tqdm starts writing
    for request in tqdm(ReviewRequest.objects.exclude(unused_reviewer__isnull=True)):
        assignment_state = map_request_state_to_assignment_state(request.state_id)
        if not (assignment_state in ('assigned', 'accepted', 'completed', 'no-response', 'overtaken', 'part-completed', 'rejected', 'withdrawn', 'unknown')):
            print(("Trouble with review_request",request.pk,"with state",request.state_id))
            exit(-1)
        ReviewAssignment.objects.create(
            review_request = request,
            state_id = assignment_state,
            reviewer = request.unused_reviewer,
            assigned_on = assigned_time(ReviewRequestDocEvent, request),
            completed_on = done_time(ReviewRequestDocEvent, request),
            review = request.unused_review,
            reviewed_rev = request.unused_reviewed_rev,
            result = request.unused_result,
            mailarch_url = request.unused_review and request.unused_review.external_url,
        )
    Document.objects.filter(type_id='review').update(external_url='')
    ReviewRequest.objects.filter(state_id__in=('accepted', 'rejected', 'no-response', 'part-completed', 'completed', 'unknown')).update(state_id='assigned')
    ReviewRequest.objects.filter(state_id='requested',unused_reviewer__isnull=False).update(state_id='assigned')

    for req_event in tqdm(ReviewRequestDocEvent.objects.filter(type="assigned_review_request",review_request__unused_reviewer__isnull=False)):
        ReviewAssignmentDocEvent.objects.create(
            time = req_event.time,
            type = req_event.type,
            by = req_event.by,
            doc = req_event.doc,
            rev = req_event.rev,
            desc = req_event.desc,
            review_assignment = req_event.review_request.reviewassignment_set.first(),
            state_id = 'assigned'
        )

    for req_event in tqdm(ReviewRequestDocEvent.objects.filter(type="closed_review_request", 
                                                               state_id__in=('completed', 'no-response', 'part-completed', 'rejected', 'unknown', 'withdrawn'),
                                                               review_request__unused_reviewer__isnull=False)):
        ReviewAssignmentDocEvent.objects.create(
            time = req_event.time,
            type = req_event.type,
            by = req_event.by,
            doc = req_event.doc,
            rev = req_event.rev,
            desc = req_event.desc,
            review_assignment = req_event.review_request.reviewassignment_set.first(),
            state_id = req_event.state_id
        )

    ReviewRequestDocEvent.objects.filter(type="closed_review_request", 
                                         state_id__in=('completed', 'no-response', 'part-completed', 'rejected', 'unknown', 'withdrawn'),
                                         review_request__unused_reviewer__isnull=False).delete()


def reverse(apps, schema_editor):
    ReviewAssignment = apps.get_model('review', 'ReviewAssignment')
    ReviewRequestDocEvent = apps.get_model('doc','ReviewRequestDocEvent')
    ReviewAssignmentDocEvent = apps.get_model('doc','ReviewAssignmentDocEvent')

    sys.stderr.write('\n')
    for assignment in tqdm(ReviewAssignment.objects.all()):
        if assignment.review_request.unused_review:
            assignment.review_request.unused_review.external_url = assignment.mailarch_url
            assignment.review_request.unused_review.save()
        assignment.review_request.state_id = assignment.state_id
        assignment.review_request.save()

    for asgn_event in tqdm(ReviewAssignmentDocEvent.objects.filter(state_id__in=('completed', 'no-response', 'part-completed', 'rejected', 'unknown', 'withdrawn'))):
        ReviewRequestDocEvent.objects.create(
            time = asgn_event.time,
            type = asgn_event.type,
            by = asgn_event.by,
            doc = asgn_event.doc,
            rev = asgn_event.rev,
            desc = asgn_event.desc,
            review_request = asgn_event.review_assignment.review_request,
            state_id = asgn_event.state_id            
        )
    ReviewAssignmentDocEvent.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('review', '0009_refactor_review_request'),
        ('doc','0011_reviewassignmentdocevent')
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
