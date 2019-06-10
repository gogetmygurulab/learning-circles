from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=128)
    page_slug = models.SlugField(max_length=256, blank=True)
    page_image = models.ImageField(blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    zoom = models.IntegerField(default=7)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    ORGANIZER = 'ORGANIZER'
    MEMBER = 'MEMBER'
    ROLES = (
        (ORGANIZER, _('Organizer')),
        (MEMBER, _('Member')),
    )
    team = models.ForeignKey('studygroups.Team', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE) # TODO should this be a OneToOneField?
    role = models.CharField(max_length=256, choices=ROLES)

    def __str__(self):
        return 'Team membership: {}'.format(self.user.__str__())


class TeamInvitation(models.Model):
    """ invittion for users to join a team """
    team = models.ForeignKey('studygroups.Team', on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE) # organizer who invited the user
    email = models.EmailField()
    role = models.CharField(max_length=256, choices=TeamMembership.ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    joined = models.NullBooleanField(null=True)

    def __str__(self):
        return 'Invitation <{} to join {}>'.format(self.email, self.team.name)


def get_study_group_organizers(study_group):
    """ Return the organizers for the study group """
    team_membership = TeamMembership.objects.filter(user=study_group.facilitator)
    if team_membership.count() == 1:
        organizers = team_membership.first().team.teammembership_set.filter(role=TeamMembership.ORGANIZER).values('user')
        return User.objects.filter(pk__in=organizers)
    return []


def get_team_users(user):
    """ Return the team members for a user """
    # TODO this function doesn't make sense - only applies for logged in users
    # change functionality or rename to get_team_mates
    team_membership = TeamMembership.objects.filter(user=user)
    if team_membership.count() == 1:
        members = team_membership.first().team.teammembership_set.values('user')
        return User.objects.filter(pk__in=members)
    return []


""" Return the team a user belongs to """
def get_user_team(user):
    team_membership = TeamMembership.objects.filter(user=user).get()
    return team_membership.team
