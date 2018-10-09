from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_group_facilitator

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.charts import LearnerGoalsChart, NewLearnersChart, CompletionRateChart, GoalsMetChart, SkillsLearnedChart, ReasonsForSuccessChart, NextStepsChart, IdeasChart, FacilitatorRatingChart, LearnerRatingChart, PromotionChart, LibraryUsageChart



# @method_decorator(user_is_group_facilitator, name='dispatch')
class StudyGroupFinalReport(TemplateView):
    template_name = 'studygroups/final_report.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupFinalReport, self).get_context_data(**kwargs)
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        learner_goals_chart = LearnerGoalsChart(study_group)
        new_learners_chart = NewLearnersChart(study_group)
        completion_rate_chart = CompletionRateChart(study_group)
        goals_met_chart = GoalsMetChart(study_group)
        skills_learned_chart = SkillsLearnedChart(study_group)
        reasons_for_success_chart = ReasonsForSuccessChart(study_group)
        next_steps_chart = NextStepsChart(study_group)
        ideas_chart = IdeasChart(study_group)
        facilitator_rating_chart = FacilitatorRatingChart(study_group)
        learner_rating_chart = LearnerRatingChart(study_group)
        promotion_chart = PromotionChart(study_group)
        library_usage_chart = LibraryUsageChart(study_group)

        context = {
            'study_group': study_group,
            'registrations': study_group.application_set.active().count(),
            'survey_responses': study_group.learnersurveyresponse_set.count(),
            'learner_goals_chart': learner_goals_chart.generate(),
            'new_learners_chart': new_learners_chart.generate(),
            'completion_rate_chart': completion_rate_chart.generate(),
            'goals_met_chart': goals_met_chart.generate(),
            'skills_learned_chart': skills_learned_chart.generate(),
            'reasons_for_success_chart': reasons_for_success_chart.generate(),
            'next_steps_chart': next_steps_chart.generate(),
            'ideas_chart': ideas_chart.generate(),
            'facilitator_rating_chart': facilitator_rating_chart.generate(),
            'learner_rating_chart': learner_rating_chart.generate(),
            'promotion_chart': promotion_chart.generate(),
            'library_usage_chart': library_usage_chart.generate(),
        }

        return context
