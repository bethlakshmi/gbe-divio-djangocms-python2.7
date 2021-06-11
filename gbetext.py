# literal text here. Please use good names, meaning short and sensible. Use
# as much comment as you need to detail where the stuff is used and for what.


# models
bid_types = (
    ('Act', 'Act'),
    ('Class', 'Class'),
    ('Costume', 'Costume'),
    ('Vendor', 'Vendor'),
    ('Volunteer', 'Volunteer'),
)
stageinfo_incomplete_warning = ("Please confirm that you have no props "
                                "requirements")

lightinginfo_incomplete_warning = "Please check your lighting info."
audioinfo_incomplete_warning = ("Please confirm that you will have no audio "
                                "playback for your performance")

conference_statuses = (
    ('upcoming', 'upcoming'),
    ('ongoing', 'ongoing'),
    ('completed', 'completed'),
)

act_format = (
    ('normal', 'normal'),
    ('summer', 'summer'),
)

landing_page_no_profile_alert = ("There's been an issue with your "
                                 "registration. Contact "
                                 "registrar@burlesque-expo.com")

phone_number_format_error = ("Phone numbers must be in a standard US format, "
                             "such as ###-###-###.")

time_format_error = "Time must be in the format ##:##."

conf_volunteer_save_error = ("There was an error saving your presentation "
                             "request, please try again.")

not_yours = "You don't own that bid."

ONSITE_PHONE = ("We need a number to reach you at during the expo. "
                "<a href=' %s '>Fix this!</a>")
EMPTY_PROFILE = ("Your profile needs an update, please review it, and save "
                 "it. <a href=' %s '>Update it now!</a>")
SCHEDULE_REHEARSAL = ('You need to schedule a rehearsal slot and/or update '
                      'act tech info for "%s". <a href = "%s">'
                      'Fix this now!</a>')

profile_alerts = {'onsite_phone': ONSITE_PHONE,
                  'empty_profile': EMPTY_PROFILE,
                  'schedule_rehearsal': SCHEDULE_REHEARSAL}

ACT_COMPLETE_NOT_SUBMITTED = ("This act is complete and can be submitted "
                              "whenever you like. "
                              "<a href = \"%s\">"
                              "Review and Submit Now </a>")
ACT_COMPLETE_SUBMITTED = ("This act is complete and has been submitted for "
                          "review.")
ACT_INCOMPLETE_NOT_SUBMITTED = ("This act is not complete and cannot be "
                                "submitted for a show.")
ACT_INCOMPLETE_NOT_SUBMITTED = ("This act is not complete but it has been "
                                "submitted for a show.")

act_alerts = {'act_complete_not_submitted': ACT_COMPLETE_NOT_SUBMITTED,
              'act_complete_submitted': ACT_COMPLETE_SUBMITTED,
              'act_incomplete_not_submitted': ACT_INCOMPLETE_NOT_SUBMITTED,
              'act_incomplete_submitted': ACT_INCOMPLETE_NOT_SUBMITTED}

act_shows_options = [(0, 'The Bordello (Fri. Late)'),
                     (1, 'The Main Event, in competition'),
                     (2, 'The Main Event, not in competition'),
                     (3, 'The Newcomer\'s Showcase')]

more_shows_options = [
    (4, 'Friday, July 28'),
    (5, 'Saturday, July 29'),
    (6, 'Sunday, July 30'),
    (7, 'Please also consider this act for GBE12, January 5-7, 2018')]

act_other_perf_options = [(0, ("Go-go dance during one or more of the shows "
                               "(we'll ask which one later)")),
                          (1, ("Be part of the opening number for The Main "
                               "Event")),
                          (2, "Model in the Fashion Show (Sunday afternoon)"),
                          (3, ("Model in the Swimsuit Show (Saturday night "
                               "late)"))]

summer_other_perf_options = [
    (0, "Go-go dance during a show"),
    (1, "Be part of the opening number."),
    (2, "Model in the Fashion Show (Saturday afternoon)")]

all_shows_options = act_shows_options + [(4, 'The Rhinestone Review')]

cue_options = [('Theater', 'Theater'),
               ('Alternate', 'Alternate'),
               ('None', 'None')]

best_time_to_call_options = [('Any', 'Any'),
                             ('Mornings', 'Mornings'),
                             ('Afternoons', 'Afternoons'),
                             ('Evenings', 'Evenings')]

states_options = [('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
                  ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
                  ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'),
                  ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
                  ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
                  ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
                  ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'),
                  ('MI', 'Michigan'), ('MN', 'Minnesota'),
                  ('MS', 'Mississippi'),
                  ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
                  ('NV', 'Nevada'), ('NH', 'New Hampshire'),
                  ('NJ', 'New Jersey'),
                  ('NM', 'New Mexico'), ('NY', 'New York'),
                  ('NC', 'North Carolina'),
                  ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
                  ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
                  ('RI', 'Rhode Island'),
                  ('SC', 'South Carolina'), ('SD', 'South Dakota'),
                  ('TN', 'Tennessee'),
                  ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
                  ('VA', 'Virginia'),
                  ('WA', 'Washington'), ('WV', 'West Virginia'),
                  ('WI', 'Wisconsin'),
                  ('WY', 'Wyoming'), ('OTHER', 'Other/Non-US')]

mic_options = (("I don't need a mic", "I don't need a mic"),
               ("I need a mic", "I need a mic"),
               ("I own a mic", "I own a mic"))

acceptance_states = ((0, 'No Decision'),
                     (1, 'Reject'),
                     (2, 'Wait List'),
                     (3, 'Accepted'),
                     (4, 'Withdrawn'),
                     (5, 'Duplicate'))

class_acceptance_states = ((1, 'Reject'),
                           (2, 'Wait List'),
                           (3, 'Accepted'))

vote_options = ((1, "Strong yes"),
                (2, "Yes"),
                (3, "Weak Yes"),
                (4, "No Comment"),
                (5, "Weak No"),
                (6, "No"),
                (7, "Strong No"),
                (-1, "Abstain"))

new_grade_options = ((4, "A"),
                     (3, "B"),
                     (2, "C"),
                     (1, "D"),
                     (0, "F"),
                     (None, "NA"),)

answer_types = (("grade", "grade"),
                ("text", "text"),
                ("boolean", "boolean"),)

festival_list = (('GBE', 'The Great Burlesque Exposition'),
                 ('BHOF', 'Miss Exotic World/Burlesque Hall of Fame'),
                 ('NYBF', 'New York Burlesque Festival'),
                 ('NOBF', 'New Orleans Burlesque Festival'),
                 ('TBF', 'Texas Burlesque Festival'))

festival_experience = (('No', 'No'),
                       ('Yes', 'Yes'),
                       ('Won', 'Yes - and Won!'))

yesno_options = (("Yes", "Yes"), ("No", "No"))
yes_no_maybe_options = (("Yes", "Yes"), ("No", "No"), ('Maybe', 'Maybe'))
boolean_options = ((True, "Yes"), (False, "No"))

video_options = (('0', "I don't have any video of myself performing"),
                 ('1', "This is video of me but not the act I'm submitting"),
                 ('2', "This is video of the act I would like to perform"))
participate_options = (('Yes', 'Yes'), ('No', 'No'), ('Not Sure', 'Not Sure'))
experience_options = (('0', "I'm not a burlesque performer"),
                      ('1', "Less than 1 year"),
                      ('2', "1-2 years"),
                      ('3', "3-4 years"),
                      ('4', "5-6 years"),
                      ('5', "more than 6 years"))

event_options = (('Special', "Special Event"),
                 ('Volunteer', "Volunteer Opportunity"),
                 ('Master', "Master Class"),
                 ('Drop-In', "Drop-In Class"),
                 ('Rehearsal Slot', 'Rehearsal Slot'))

new_event_options = (('Special', "Special Event"),
                     ('Master', "Master Class"),
                     ('Drop-In', "Drop-In Class"),
                     ('Rehearsal Slot', 'Rehearsal Slot'))

class_options = (('Lecture', "Lecture"),
                 ('Movement', "Movement"),
                 ('Panel', "Panel"),
                 ('Workshop', "Workshop"))

length_options = ((30, "30"),
                  (60, "60"),
                  (90, "90"),
                  (120, "120"))

class_length_options = ((60, "60"),
                        (90, "90"),
                        (120, "120"))

space_options = (('Movement Class Floor',
                  (("0", "Don't Care about Floor"),
                   ("1", "Carpet"),
                   ("2", "Dance Floor"),
                   ("3", "Both"))),
                 ('Lecture Class Setup',
                  (("4", "Don't Care about Seating"),
                   ("5", "Lecture Style - tables and chairs face podium"),
                   ("6", "Conversational - seating in a ring"))))

schedule_options = (('Preferred Time', "Preferred Time"),
                    ('Available', "Available"),
                    ('Not Available', "Not Available"))
time_options = (('Morning', "Morning (before noon)"),
                ('Early Afternoon', "Early Afternoon (12PM-3PM)"),
                ('Late Afternoon', "Late Afternoon (3PM-6PM)"))
day_options = (('Fri', "Friday"),
               ('Sat', "Saturday"),
               ('Sun', "Sunday"))
system_options = [
    (0, 'local/debug'),
    (1, 'test/live')]
source_options = [
    (0, 'Paypal'),
    (1, 'Brown Paper'),
    (2, 'Eventbrite')]
role_options = (
    ('Interested', "Interested"),
    ('Moderator', "Moderator"),
    ('Panelist', "Panelist"),
    ('Performer', "Performer"),
    ('Producer', "Producer"),
    ('Staff Lead', "Staff Lead"),
    ('Teacher', "Teacher"),
    ('Technical Director', "Technical Director"),
    ('Volunteer', "Volunteer"),
    ('Rejected', "Rejected"),
    ('Waitlisted', "Waitlisted"),
    ('Pending Volunteer', "Pending Volunteer"),)
role_commit_map = {
    'New': (5, "fas fa-plus-square gbe-text-secondary"),
    'Error': (0, "fas fa-exclamation-triangle gbe-text-warning"),
    'Interested': (1, "fas fa-check-circle gbe-text-success"),
    'Moderator': (1, "fas fa-check-circle gbe-text-success"),
    'Panelist': (1, "fas fa-check-circle gbe-text-success"),
    'Performer': (1, "fas fa-check-circle gbe-text-success"),
    'Producer': (1, "fas fa-check-circle gbe-text-success"),
    'Staff Lead': (1, "fas fa-check-circle gbe-text-success"),
    'Teacher': (1, "fas fa-check-circle gbe-text-success"),
    'Technical Director': (1, "fas fa-check-circle gbe-text-success"),
    'Volunteer': (1, "fas fa-check-circle gbe-text-success"),
    'Rejected': (4, "fas fa-window-close gbe-text-danger"),
    'Waitlisted': (2, "fas fa-clock gbe-text-info"),
    'Pending Volunteer': (3, "fas fa-hourglass-half gbe-text-info")}
not_scheduled_roles = ["Pending Volunteer", "Waitlisted", "Rejected"]
volunteer_action_map = {
  'approve': {'role': "Volunteer", 'state': 3},
  'waitlist': {'role': "Waitlisted", 'state': 2},
  'reject': {'role': "Rejected", 'state': 1},
}
act_casting_label = "Section"

vend_time_options = (
    (" ",
     " "),
    ('Saturday & Sunday, noon to 8pm ONLY.',
     "Saturday & Sunday, noon to 8pm ONLY."))
ad_type_options = (("Full Page, Premium", "Full Page, Premium"),
                   ("Full Page, Interior", "Full Page, Interior"),
                   ("Half Page, Premium", "Half Page, Premium"),
                   ("Half Page, Interior", "Half Page, Interior"),
                   ("Quarter Page, Premium", "Quarter Page, Premium"),
                   ("Quarter Page, Interior", "Quarter Page, Interior"))

num_panel_options = (
    ("One Panel",
     "One Panel ($30 includes application fee)"),
    ("Two Panels",
     "Two Panels ($75; if your work is not accepted, $45 will be refunded)"),
    ("Sculpture",
     "My artwork is sculptural and needs to be displayed on a table " +
     "($30 includes app. fee)"))

class_proposal_choices = [
    ('Class', 'Class'),
    ('Panel', 'Panel'),
    ('Either', 'Either')]

###############
#  Static Text options for the Scheduler
###############
#    Options for schedule blocking
blocking_text = (('False', False), ('Hard', 'Hard'), ('Soft', 'Soft'))

#    Options for time types
time_text = (('Start Time', 'Start Time'),
             ('Stop Time', 'Stop Time'),
             ('Hard Time', 'Hard Time'),
             ('Soft Time', 'Soft Time'))

event_labels = {'type': 'Type',
                'fee': 'Materials Fee',
                'parent_event': 'Part of',
                'volunteer_category': 'Opportunity Category'
                }

overlap_location_text = ' (alt)'


calendar_type = {0: 'General',
                 1: 'Conference',
                 2: 'Volunteer'}

calendar_for_event = {
    'Special': "General",
    'Volunteer': "Volunteer",
    'Master': "General",
    'Drop-In': "General",
    'Staff Area': None,
    'Rehearsal Slot': None,
    'Class': 'Conference',
    'Show': 'General'
}

email_template_desc = {
    'submission notification': '''This email is sent to reviewers when a(n) \
    %s is submitted and ready for review.''',
    'No Decision': '''This email is sent to a bidder when the coordinator \
    sets the %s to the state "No Decision"''',
    'Reject': '''This email is sent to the bidder when the coordinator \
    rejects the %s''',
    'Wait List': '''This email is sent to the bidder when the %s is put on a \
    wait list.''',
    'Accepted': '''This email is sent to the bidder when the %s has been \
    accepted.''',
    'Withdrawn': '''This email is sent to the bidder when the %s has been \
    withdrawn.''',
    'Duplicate': '''This email is sent to the bidder when the coordinator \
    marks the %s as a duplicate''',
    'act accepted': '''This email is sent to the performer when they have \
    been cast into the show %s.''',
}

unique_email_templates = {
    'volunteer': [
        {'name': 'volunteer schedule update',
         'description': '''This email is sent to volunteers when \
         their schedule has been updated''',
         'category': 'volunteer',
         'default_base': "volunteer_schedule_update",
         'default_subject':
            "A change has been made to your Volunteer Schedule!", },
        {'name': 'volunteer update notification',
         'description': '''This email is sent to reviewers \
         when a volunteer updates their offer to volunteer.''',
         'category': 'volunteer',
         'default_base': "bid_submitted",
         'default_subject': "Volunteer Update Occurred", },
        {'name': 'volunteer changed schedule',
         'description': '''This email is sent to the Volunteer Coordinator \
         and the Staff Lead(s) of the changed event, when a volunteer has \
         added or removed an event they have/had volunteered for.  This \
         includes pending requests for events requiring approval.  It also \
         shows any conflict warnings or other errors associated with the \
         schedule change.  NOTE - at present, it does NOT mail to the leads \
         of the previous commitment in a case of conflict.''',
         'category': 'volunteer',
         'default_base': "volunteer_schedule_change",
         'default_subject': "Volunteer Schedule Change", }],
    'scheduling': [
        {'name': 'daily schedule',
         'description': '''This email is sent daily to any user with a \
         schedule obligation the next day.''',
         'category': 'scheduling',
         'default_base': "schedule_letter",
         'default_subject':
            "Your Schedule for Tomorrow at GBE", }, ],
    'registrar': [
        {'name': 'unsubscribe email',
         'description': '''This email is sent to the email of the user when
         someone requests to unsubscribe w/out logging in.''',
         'category': 'registration',
         'default_base': "unsubscribe_email",
         'default_subject':
            "Unsubscribe from GBE Mail", }, ],
}

default_class_submit_msg = "Your class was successfully submitted"
default_class_draft_msg = "Your draft was successfully saved"
default_act_submit_msg = "Your act was successfully submitted"
default_act_draft_msg = "Your draft was successfully saved"
default_costume_submit_msg = "Your costume was successfully submitted"
default_costume_draft_msg = "Your draft was successfully saved"
default_propose_submit_msg = "Your idea was successfully submitted"
default_vendor_submit_msg = "Your vendor proposal was sucessfully submitted"
default_vendor_draft_msg = "Your draft was successfully saved"
default_submit_msg = "Thank you for submitting your bid."
invalid_volunteer_event = '''The following event is not currently available.  \
It may have just reached a maximum number of volunteers. Unavailable event is \
'''
fee_instructions = '''<a href="%s" target="_blank">Make Payment at \
Brown Paper Tickets</a><br>Our records show that you have not paid your \
related fees.  You can pay at Brown Paper Tickets by pressing the "Pay Fee" \
button below.  Once the fee is paid, please return to this form and submit \
your draft.  In the meantime, pressing either button will safe a draft of \
your application.'''
bid_not_submitted_msg = '''The bid has not yet been submitted.  Edit and \
submit the bid using the button below.'''
bid_not_paid_msg = '''Payment for your submission has not yet been received.  \
If you've just paid with PayPal, this page should update in a minute or two.  \
If your bid is not updated in 5 minutes or less, please contact us.<br><br>  \
If you have not paid, use the button below to edit the bid and proceed to \
payment.'''
payment_needed_msg = '''
<FONT SIZE="+2">
Thank you for submitting your work for The Great Burlesque Expo!</FONT>

<P><font color=red>This draft has not yet been submitted.</font><P>

<H3>Fee has not been Paid</H3>

Thank you for participating in The Great Burlesque Exposition!  Our records \
show that you have not paid your related fees.  You can pay at Brown Paper \
Tickets by following the below link.<br><br>

If you have just paid the fee, please note it may take up to 30 minutes \
to show in our system.  If, after 1 hour, you continue to have problems, \
please <a href="/get-touch">contact us</a> for help with your problem.<br><br>

<a href="%s" target="_blank">Make Payment at Brown Paper Tickets</a>
<br><br>
The steps to successfully submitting a bid are:<br><br>
1) Pay your application fee.  This happens at BrownPaper Tickets (in another \
window).  Once you've paid your fee, you'll be able to create a draft \
application, save it and revise it until you're satisfied with it, and then \
submit it.  Once your application fees and application have been submitted, \
you won't be able to revise or edit your application (but you will be able to \
view it so you what information you applied with!)<br>
2) Fill out your application<br>
3) Click "save Draft".  You'll see your application listed in your personal \
pane with the notation "click to edit".<br>
4) Re-read your application to make sure you're happy with it and all \
required information is complete.<br>
5) Click "Submit Application".  Once you click "Submit Application" you will \
not be able to edit or revise your application!<br>
6) Your successfully submitted application will be viewable as a link in your \
personal pane; it'll be displayed with a link which says "click to view", but \
you will no longer be able to edit it.<br>
<br>
If you encounter an error which seems to indicate that you haven't paid your \
application fee, please wait 5 minutes and re-submit your application (go to \
your personal pane, click "Click to Edit", and once your information is \
displayed, click the "Submit" button).  If the problem persists, please \
contact the registrar.<br>
'''
default_clone_msg = "You have successfully made a new copy."
default_update_profile_msg = "Your profile has been updated."
link_sent_msg = '''The request to send an unsubscribe link was received.  If \
there is a valid user account available, a link will be sent to the email \
provided.'''
bad_token_msg = '''This link is either expired or invalid.  Get a new link \
emailed to you on this page'''
default_create_persona_msg = "Your persona has been created."
default_edit_persona_msg = "Your persona has been updated."
default_create_business_msg = "Your business has been created."
default_edit_business_msg = "Your business has been updated."
default_edit_troupe_msg = "Your troupe has been updated."
troupe_header_text = '''More than 1 person, who will be performing on stage \
together.'''
default_advanced_acttech_instruct = '''The following information is optional.\
  If your act does not need this information, there is no need to complete \
this form.'''
default_basic_acttech_instruct = '''These are the basic details our crew \
needs for lighting, playing audio, and making sure the stage is set.'''
default_rehearsal_acttech_instruct = '''Reserve your rehearsal slot early.  \
technical details about your act can be added later.'''
default_rehearsal_booked = '''Rehearsal is booked.'''
rehearsal_book_error = '''The rehearsal could not be booked.  If this issue \
persists, please contact GBE support.'''
default_act_tech_advanced_submit = "All of your act tech details have been \
submitted."
default_act_tech_basic_submit = "Your basic act tech details have been \
submitted.  Stay tuned, later on you\'ll be asked for further information."
default_update_act_tech = "Your Act Technical Details have been updated."
default_act_title_conflict = '''You've aready created a draft or made a \
submission for this act.  View or edit that act here:  <a href="%s">%s</a>'''
act_not_unique = '''Please name this act with a different title, \
or edit the existing act.'''
no_casting_msg = '''The casting role you've specified is not one our defined \
roles.  Check the dropdown and try again.'''
act_status_change_msg = "Act status has been changed."
act_status_no_change_msg = "Act status has not been changed."
no_persona_msg = '''A troupe must have at least one member, please enter your
 stage name and performer bio.  Troupe activities will be shown on your
 schedule and the schedule of any other member.'''
no_profile_msg = '''Your profile is not complete, you must provide a first \
and last name, a name we can use on your badge, and a phone number we can \
use to notify you of changes to the schedule at run time.'''
no_login_msg = '''Please set up and account and give us some ways to \
contact you, or login, if you already have an account.'''
full_login_msg = '''%s - <a href="%s">Login</a>'''
default_deactivate_profile_admin_msg = '''This user is involved in one or \
more activities on this site.  To protect unintended changes, the user was \
deactivated.  To delete, reactivate, or review the details, go to the admin: \
'''
default_delete_profile_admin_msg = '''No relevant site data found, this user \
has been completely deleted'''
default_act_review_error_msg = '''There was an issue with processing your act \
review for act %s, see below for details and please resubmit.'''
default_act_review_success_msg = '''You have successfully reviewed act %s, \
from performer %s.'''
fashion_fair_intro = '''<b>The Great Burlesque Exposition</b> offers two \
different (but equally fabulous!) types of shopping experience! First, is \
our <I>Vintage Fashion Fair</I>, located on the first floor in the \
President's Ballroom, next door to the theater.  Open on Saturday and Sunday, \
from noon until 8:00 p.m., it's home to dozens of delightful vendors selling \
everything you need, whether you're a professional performer or just want to \
look spectacular!<P><I>The Vintage Fashion Fair</I> is also home to our \
<B>Costume Display</b>, our <B>Art Exhibit</b>, and our <B>Caf&eacute;</B>. \
<P>Feeling peckish between classes? Want to grab a quick snack or beverage? \
No need to run out into the cold or even up to the hotel restaurant! \
Attendees of <I>The Great Burlesque Exposition</I> can fortify themselves \
with soups, wraps, fresh fruit, and more... all at very reasonable prices!'''
email_pref_note = '''Your privacy is very important to us. We promise that \
your information will not be sold or traded. That said, we need your complete \
and accurate contact information in order to alert you to important aspects \
of the event: your ticket purchases and personal schedule, news, events, and \
deadlines. Your profile information will be visible to the department head \
associated with any role or activity you've elected to be involved with (that \
is, if you're performing, our selection committee and stage managers will be \
able to see your profile information. If you're teaching, the conference \
committee members and staff will be able to see your profile information, \
etc.).'''
send_link_message = '''This site could not verify the email unsubscribe link. \
Please enter your email and a new link will be mailed to you.'''
admin_note = '''Use the BPT Purchase Email item to fix cases where the Brown\
 Paper Tickets purchase was made under a different email.  Please handle email\
 information with care and do not distribute or use for any purpose outside of\
 Expo communication.'''
save_email_template_success_msg = '''The email template has been saved.  \
Your updates will be applied to all future automated messages using this \
template.  The Email Template name is '''
send_email_success_msg = '''A mail was successfully sent to '''
unsubscribe_text = '''<br><br><div style="text-align: center;"><small> \
This email has been sent by the burlesque-expo.com email system<br> \
<a href="http://%s%s">Update email preferences</a><small></div>'''
unsub_footer_include = "{% include 'gbe/email/unsub_footer.tmpl' %}"
unsub_footer_plain_include = \
    "{% include 'gbe/email/unsub_footer_plain.tmpl' %}"
to_list_empty_msg = '''No recipients were found for your search criteria.  \
                    Please try something else'''
unknown_request = '''This request makes no sense'''
group_filter_note = '''The recipients listed here include only active users,
who have agreed to be contacted by the Expo.  Disabled users and users who
have set their preference to not receive email of this kind will not be
included.'''
intro_transaction_message = '''Transactions marked in blue are associated \
with the "limbo" user as a placeholder, because no user matching the \
purchaser's email could be found.'''
import_transaction_message = '''A sync was attempted, check the logs for \
errors, if 0 transactions were recieved, it can mean we are up to date, it \
can mean we failed to import any.'''
intro_ticket_message = '''The tickets below are all the ticket events & items \
available for the current conference.'''
intro_ticket_assign_message = '''This grid shows what tickets are connected \
to which GBE event.'''
org_id_instructions = '''The organization id has not been defined.  Go to \
admin and set one of the following ids in the EventbriteSettings for \
'organization_id' for debug or live.  Only events for this organization \
will be synced.'''
sync_off_instructions = '''%s ticketing system is not currently syncing.  \
This can be changed on the settings page in the admin.'''
eventbrite_error = '''There was an error in contacting eventbrite.  Status: \
%d, Message: %s'''
no_settings_error = '''There are no Eventbrite settings for this server.  Go \
to admin and ticketing -> EventbrightSettings and enter settings.  Oauth 
token can be found in the API settings in EventBrite.  After that, return
here to get the organization id.'''
intro_bptevent_message = '''This page makes an 'event' in the sense of BPT \
events.  For Paypal, it's simply a container for a set of prices.  These \
containers define payment for act fees, vendor fees, or entry into the expo \
for all or some events.'''
intro_make_ticket_message = '''This page makes an individual ticket (and \
price) for either a fee or entry into the expo.  The BPT Event connected to \
this ticket defines what the customer gets when they pay for the ticket.'''
edit_event_message = '''Event has been successfully updated.'''
edit_ticket_message = '''Ticket has been successfully updated.'''
delete_ticket_fail_message = '''Deletion failed, transactions exist for this \
ticket.'''
delete_ticket_success_message = '''The ticket was successfully deleted (no \
transactions found).'''
delete_event_success_message = '''The BPT Event was successfully deleted (no \
transactions for any ticket found).'''
delete_event_fail_message = '''Deletion failed, transactions exist for tickets \
for this event.'''
link_event_to_ticket_success_msg = '''Successfully linked the following \
                                   tickets: '''
unlink_event_to_ticket_success_msg = '''Successfully disconnected the  \
following tickets from events: '''
create_ticket_event_success_msg = "Created and linked a new BPT Event: "
no_tickets_found_msg = '''No tickets could be found for the bpt event id.  \
Check the BPT Event id and your connection to Brown Paper Tickets.  With no \
tickets listed, users will be unable to purchase entrance to this event.'''
payment_details_error = '''Your choice for fee selections was not valid, \
please check the form and try again.'''
set_volunteer_role_summary = "Volunteer Offer %s"
set_volunteer_role_msg = "Volunteer offer has been set to %s: <br/>"
set_favorite_msg = '''Your interest has been set and will appear on your \
                   personal schedule.'''
unset_favorite_msg = '''Your interest has been removed and will no longer \
                   appear on your personal schedule.'''
set_volunteer_msg = '''Thank you!  This volunteer shift has been added to \
your schedule.'''
unset_volunteer_msg = '''Sorry to see you go!  This volunteer shift has been \
removed from your personal schedule.'''
set_pending_msg = '''Thank you!  Your offer to volunteer has been sent and is \
awaiting approval.'''
unset_pending_msg = '''Sorry to see you go!  Your offer to volunteer has \
been deleted.'''
volunteer_instructions = '''Click on any event to see details and offer to \
volunteer.  Events that show a white box are immediately available.  Events \
with a highlighted box require approval, when you volunteer, your offer will \
be reviewed and a response will be sent shortly.'''
pending_note = '''This is a shift that requires approval.  When you volunteer,\
 your offer will be reviewed and a response will be sent shortly.'''
interested_explain_msg = '''Anyone with an account with The Great Burlesque \
Exposition can show their interest in an event and add it to their schedule \
by clicking on the star on our calendar or in an event description.  Starred \
events will show up in their personal calendars.  Showing interest is not a \
firm commitment to attend and it does not imply that the person has purchased \
a valid ticket or pass to attend the class or the conference.<br><br>Want \
more interested attendees?  We fully endorse shameless promotion! Post your \
event page to your fans on social media, email, your website or anywhere and \
get the word out!'''
interested_report_explain_msg = '''This list includes all scheduled \
classes and provides a count of how many logged in users have shown interest \
in the class.  Interest does not reflect a firm commitment, nor does it \
imply anything about ticket purchase.'''
not_ready_for_eval = '''Our apologies, but we're not ready to take in \
evaluations right now, please come back soon!'''
one_eval_msg = '''We can only accept one evaluation per person, per event.'''
eval_success_msg = '''Your evaluation was successfully submitted.  Thanks \
for your feedback!'''
eval_intro_msg = '''Thanks for your feedback!  Please grade your class \
experience and let just know any additional comments in the box below.  \
Teachers will get a summary of the review results, but the results will be \
anonomized unless you check the box saying it's OK to share your info.'''
eval_report_explain_msg = '''This is a summary of all class evaluations for \
this conference.  Please be cognizant of responder sensitivity when sharing \
participant names and details.  This view is NOT available to teachers.'''
not_purchased_msg = '''You have not purchased a ticket for either a Whole \
Shebang or conference attendance, so you can't rate this class.  Check \
your homepage - if our records are incorrect, please let us know.'''
volunteer_allocate_email_fail_msg = '''The system was not able to send email \
to the volunteer.  Check the email template, try again, or mail the volunteer \
manually.  If the issue persists, please contact the web admin.'''
bidder_email_fail_msg = '''The system was unable to send an email notifying \
the bidder of the updates you have made.  Check the email template, try \
again, or mail the bidder manually.  If the issue persists, please contact \
the web admin.'''
eval_as_presenter_error = '''You cannot evaluate a class in which you were \
the Teacher, Moderator or Panelist.  If you have feedback regardling your \
class, please contact the coordinator directly.'''
parent_event_delete_warning = '''This scheduled event is a parent to other \
schedule items.  These schedule items have not been deleted, and will remain \
on the calendar.'''
no_conf_day_msg = '''The target conference has not been properly configured. \
Specify the days for this conference before proceeding.'''
rehearsal_delete_msg = '''This rehearsal slot was deleted.  If any acts were \
booked for this slot, they will be warned on their account page to fine a new \
slot.'''
copy_solo_intro = '''Choosing a target day to copy MUST be selected if the \
parent event is not chosen.  If parent event is chosen, this overrides the \
day choice.  WARNING - be sure to choose events, staff areas, and days from \
the same conference or results can be unpredictable.  Only upcoming \
conference options are shown.'''
user_messages = {
    "THEME_INSTRUCTIONS": {
        'summary':  "Instructions at top of theme edit page",
        'description': '''This page displays the current saved styles of the
        theme being edited.  Update it to get an update to this page's
        style.'''
    },
    "CLONE_INSTRUCTIONS": {
        'summary':  "Instructions at top of theme clone page",
        'description': '''Enter the name, version number and settings to make,
        a new version.  Current style settings are a copy of the theme being
        cloned.'''
    },
    "LAST_THEME": {
        'summary':  "Can't Delete Last Theme",
        'description': '''This is the last theme in the system.  It cannot be
        deleted until another theme is created.'''
    },
    "CURRENTLY_ACTIVE": {
        'summary':  "Can't Delete Active Theme",
        'description': '''This theme is currently active on live, test or both.
        Before deleting the theme, you must activate a different theme for
        both environments.'''
    },
}
troupe_intro_msg = '''This list includes only Troupes with active contacts \
(i.e. the person who entered this troupe in our system is an active user). \
Contact an administrator if a troupe you are looking for is not visible.  \
Inactive troupe members are also filtered from the membership list.'''
profile_intro_msg = '''This list includes only active users.  Inactive users \
can be viewed only in the administration pages.  To reactivate a missing \
user, contact an admin.  Troupes owned by a user are shown in parenthesis \
under the user's name.'''
change_day_note = '''Change the day on any current/upcoming conference.  Pick
the new start day and all conference days will be moved and all events will be
updated.  This assumes that the conference is the same number of days long.'''
missing_day_form_note = '''Could not load the form for the identified day.
  This may be because the day is for a past conference.'''
