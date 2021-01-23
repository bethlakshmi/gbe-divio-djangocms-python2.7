# literal text from gbe forms
# see gbetext.py for the rules
# until I copy them over

participant_labels = {
    'legal_first_name': ('Legal First Name'),
    'legal_last_name': ('Legal Last Name'),
    'display_name': ('Badge Name'),
    'address1': ('Street Address'),
    'address2': ('Street Address (cont.)'),
    'best_time': ('Best time to call'),
    'offsite_preferred': ('Offsite phone'),
    'how_heard': "How did you hear about The Expo?",
    'purchase_email': ('BPT Purchase Email'),
}

profile_preferences_help_texts = {
    'in_hotel':  'It is helpful for us to know who\'s staying in the hotel.',
    'send_daily_schedule':  '''We'll mail you your schedule for the next day \
        (on Friday, you get Saturday's schedule). This includes any classes \
        you are teaching or have expressed interest in, any volunteer shifts, \
        any scheduled rehearsals, etc. Opting out will disable this \
        feature.''',
    'send_bid_notifications':  '''If you have applied to teach, volunteer, or \
        perform in the past, we may reach out to you to see if you want do \
        one or more of those things again. Opting out will keep you from \
        receiving those emails, but will not prevent you from getting \
        individual emails about your current commitments.''',
    'send_role_notifications':  '''If you have taught, volunteered, performed,\
        sold stuff, or displayed stuff in the past, we may reach out to you to\
        see if you want do one or more of those things again. Opting out will \
        keep you from receiving those emails, but will not prevent you from \
        potentially getting individual emails about your current \
        commitments.''',
    'send_schedule_change_notifications':  '''The GBE system will \
        automatically email you when a part of the expo you are interested \
        or participating in has changed.  Turning off this item will \
        automatically disable that automated notification.''',
}

profile_preferences_labels = {
    'inform_about': 'Please let me know about...',
    'in_hotel': 'I am staying at the hotel',
    'show_hotel_infobox': ('Show hotel booking info on your landing page?'),
    'send_daily_schedule': ('Send me my schedule'),
    'send_bid_notifications': (
      'Email me based on my past and current proposals'),
    'send_role_notifications': (
      'Email me based on my past and current activities'),
    'send_schedule_change_notifications': (
      'Email me when my schedule at GBE changes'),
}

event_type_options = [(
    'Classes', (
        ('drop-in', 'Drop-In Class'),
        ('conference', 'Conference Class'),
        ('master', 'Master Class'), ), ), (
    'Other Public Events', (
        ('show', 'Show'),
        ('special', 'Special Event'), ), ), (
    'Behind the Scenes', (
        ('rehearsal', 'Rehearsal Slot'),
        ('staff', 'Staff Area'),
        ('volunteer', 'Volunteering'), ), ), ]

event_settings = {
    'drop-in': {
        'event_type': 'Drop-In Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Staff Lead', 'Teacher', 'Volunteer', ],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'master': {
        'event_type': 'Master Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Teacher', 'Volunteer', ],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'show': {
        'event_type': 'Show',
        'second_title': 'Make New Show',
        'volunteer_scheduling': True,
        'roles': ['Producer', 'Technical Director', ],
        'max_volunteer': 1,
        'open_to_public': True,
    },
    'special': {
        'event_type': 'Special Event',
        'second_title': 'Make New Special Event',
        'volunteer_scheduling': True,
        'roles': ['Staff Lead', ],
        'max_volunteer': 1,
        'open_to_public': True,
    },
    'staff': {
        'event_type': 'Staff Area',
        'second_title': 'Make New Staff Area',
        'volunteer_scheduling': True,
        'roles': ['Staff Lead', ],
        'max_volunteer': 1,
        'open_to_public': False,
    },
    'volunteer': {
        'event_type': 'Volunteer Opportunity',
        'second_title': 'Make New Volunteer Opportunity',
        'volunteer_scheduling': False,
        'roles': [],
        'max_volunteer': 1,
        'open_to_public': False,
    },
    'panel': {
        'event_type': 'Conference Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Moderator', 'Panelist', 'Panelist', 'Panelist', 'Panelist'],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'lecture': {
        'event_type': 'Conference Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Teacher', 'Teacher', 'Teacher'],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'movement': {
        'event_type': 'Conference Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Teacher', 'Teacher', 'Teacher'],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'workshop': {
        'event_type': 'Conference Class',
        'second_title': 'Make New Class',
        'volunteer_scheduling': False,
        'roles': ['Teacher', 'Teacher', 'Teacher'],
        'max_volunteer': 0,
        'open_to_public': True,
    },
    'rehearsal slot': {
        'event_type': 'Rehearsal Slot',
        'second_title': 'Make New Rehearsal Slot',
        'volunteer_scheduling': False,
        'roles': [],
        'max_volunteer': 1,
        'open_to_public': False,
    },
}
role_map = {
    'Staff Lead': False,
    'Moderator': True,
    'Teacher': True,
    'Panelist': True,
    'Volunteer': False,
    'Producer': False,
    'Technical Director': False,
}
all_roles = ["Staff Lead", "Schedule Mavens", "Registrar"]
role_option_privs = {
    'Producer': ["Interested",
                 "Performer",
                 "Volunteer",
                 "Staff Lead",
                 "Technical Director",
                 "Producer"],
    'Technical Director': ["Interested",
                           "Performer",
                           "Volunteer",
                           "Staff Lead",
                           "Technical Director",
                           "Producer"],
    'Act Coordinator': ["Interested",
                        "Performer",
                        "Technical Director",
                        "Producer"],
    'Class Coordinator': ["Interested",
                          "Panelist",
                          "Teacher",
                          "Moderator"],
    'Volunteer Coordinator': ["Interested", "Volunteer", "Staff Lead"],
}
event_collect_choices = [
                ("Conference", "All Conference Classes"),
                ("Drop-In", "All Drop-In Classes"),
                ("Volunteer", "All Volunteer Events")]
copy_mode_labels = {
    'copy_mode': "How would you like to copy this event?",
    'room': "Choose the default room"
}
copy_mode_choices = [
    ("copy_children_only",
     "Copy all sub-events to "),
    ("include_parent",
     "Include this event and all sub events, make new event on ")
]
copy_errors = {
    'room_conf_mismatch': "This room is not available for the conference on " +
    "this day.",
    'no_target': " Must choose the target event when copying sub-events.",
    'no_day': " Must choose a day when copying all events.",
    'room_target_mismatch': "This room is not available for the conference " +
    "of the chosen event."
}
inform_about_options = [('Exhibiting Art or Costumes',
                         'Exhibiting Art or Costumes'),
                        ('Performing', 'Performing'),
                        ('Pre-event Organizing', 'Pre-event Organizing'),
                        ('Sponsoring/Advertising', 'Sponsoring/Advertising'),
                        ('Teaching', 'Teaching'),
                        ('Vending', 'Vending'),
                        ('Volunteering', 'Volunteering at the Expo')]

how_heard_options = [('Previous attendee', 'Attended Previously'),
                     ('B.A.B.E.', 'B.A.B.E.'),
                     ('Facebook', 'Facebook'),
                     ('Received a direct email', 'Received a direct email'),
                     ('Saw a postcard', 'Saw a postcard'),
                     ('Saw a print ad', 'Saw a print ad'),
                     ('Word of mouth', 'Word of mouth'),
                     ('Yahoo! Group', 'Yahoo! Group'),
                     ('Other', 'Other')]

participant_form_help_texts = {
    'display_name': ('The name you want to be known by as an Expo participant. \
    This can be a stage name, or your real-world name, or anything that you \
    want to have printed on your Expo badge and other official Expo \
    communications. This defaults to your First and Last Name.'),
    'phone': ('A phone number we can use to reach you when you are at the \
    Expo, such as cell phone.'),
    'offsite_preferred': ('Your preferred phone number (if different from \
    above), for communication before the Expo.  Use this if you prefer to \
    get phone calls at a phone you cannot bring to the Expo.'),
    'legal_name': ('Please provide us with your legal first and last names.\
     This information is only used by the event staff never shared with anyone\
     without your prior permission.\
     Please use your stage name in the Badge Name field.'),
}


phone_validation_error_text = (
    'If Preferred contact is a Phone call or '
    'Text, we need your phone number as either an Onsite phone or Offsite '
    'preferred.')


troupe_header_text = '''More than 1 person, who will be performing on stage \
together.'''

event_create_text = {
    'GenericEvent': '''Enter the details for a new event.  A generic event \
    can be event that is not a show or a conference class.  Be sure to set \
    the type of event properly as each type is displayed differently in \
    the public website.''',
    'Show': '''Enter the details for a new show.  Shows are displayed on show \
    listings, but if you are adding a show and want specialized menu items, \
    please contact the web web team.  REMINDER:  For linking to show tickets, \
    you must also use the ticketing section to link tickets.''',
    'Class': '''Enter the details for a new class.  This is specifically for \
    conference classes.  For Master Classes and Drop-In classes, please use \
    Generic Events.'''}

event_help_texts = {
    'type': '''Special Events, Master Classes, and Drop In classes are shown in \
    event lists, Staff Areas do not..''',
    'cue_sheet': '''These are the lighting options that performers will be \
    able to choose when they submit their act tech info.  These options are \
    variable based on what theater the show is booked into and how it's \
    lighting is dsigned.  "Theater" is the arrangement we use in the main \
    stage, and "Alternate" fits with the vendor room stage.'''}

event_labels = {
    'e_title': 'Title',
    'e_description': 'Description'}

volunteer_availability_options = [('SH0', 'Thursday evening (6PM-11PM)'),
                                  ('SH8', 'Saturday late night (10PM-1AM)'),
                                  ('SH1', 'Friday morning (9AM-12PM)'),
                                  ('SH9', 'Sunday morning (8AM-12PM)'),
                                  ('SH2', 'Friday afternoon (12PM-6PM)'),
                                  ('SH10', 'Sunday afternoon (12PM-6PM)'),
                                  ('SH3', 'Friday night (5PM-10PM)'),
                                  ('SH11', 'Sunday night (5PM-10PM)'),
                                  ('SH4', 'Friday late night (10PM-1AM)'),
                                  ('SH12', 'Strike Crew (10PM-1AM)'),
                                  ('SH5', 'Saturday morning (8AM-12PM)'),
                                  ('SH13', 'Monday morning (9AM-12PM)'),
                                  ('SH6', 'Saturday afternoon (12PM-6PM)'),
                                  ('SH7', 'Saturday night (5PM-10PM)')]

volunteer_labels = {
    'number_shifts': 'How many hours would you like to work?',
    'opt_outs': 'Are there events that we should make sure to not schedule \
        you during?',
    'pre_event': 'Are you interested in helping with pre-event tasks?',
    'background': 'Tell us about your background, including relevant skills \
        and experience'

}

volunteer_help_texts = {
    'pre_event': ('Pre-event tasks could be anything from marketing \
    to logistics to advertising sales to data entry. In short, \
    anything we need done before the BurlExpo starts'),
    'volunteer_availability_options': ('These times are general guidelines.  \
    If there are specific times that you cannot work, please let us know \
    in the box below.')
}

available_time_conflict = \
    'Available times conflict with unavailable times.  Conflicts are: %s'

unavailable_time_conflict = \
    'Unavailable times conflict with Available times.'

phone_error1 = ['Phone number needed here']
phone_error2 = ['... or here ']
phone_error3 = ['...or choose a contact method that does not require a phone.']

tech_labels = {
    'track_title': 'Name of Song',
    'track_artist': 'Name of Song Artist',
    'duration': 'Length of Act',
    'primary_color': ('Primary color of your costume'),
    'secondary_color': ('Secondary color of your costume'),
    'feel_of_act': ('Describe the mood of your act'),
    'clear_props': ('I will leave props or set pieces on-stage that will '
                    'need to be cleared'),
    'crew_instruct': ('Notes for Stage Crew:'),
    'introduction_text': ('Introductory Text for MC'),
    'read_exact': ('Please read my intro exactly as written.'),
    'pronouns': ('Preferred Pronouns'),
    'prop_setup': 'Staging Info',
    'mic_choice': 'Microphone Choice',
    'start_blackout': 'Start with the stage blacked out',
    'end_blackout': 'End with the stage blacked out',
}
prop_choices = [
    ('I have no props or set pieces', 'I have no props or set pieces'),
    ('I have props I will need set before my number',
     'I have props I will need set before my number'),
    ('I have props I will need a stage kitten to hand me or take from me '
     'during my number',
     'I have props I will need a stage kitten to hand me or take from me '
     'during my number'),
    ('I will need to interact with the Stage Kitten during my number '
     '(i.e., I need another body on stage',
     'I will need to interact with the Stage Kitten during my number '
     '(i.e., I need another body on stage'),
    ('I will leave props or set pieces on-stage that will need to be cleared',
     'I will leave props or set pieces on-stage that will need to be cleared'),
]
tech_help_texts = {
    'duration': 'Length of act expressed as mm:ss',
    'feel_of_act': (
        'This is for our lighting crew. Describe the tone of your act in a ',
        'few short phrases. Is your act happy? Silly? Like an old movie? ',
        'Set outdoors? Please don\'t just say "sexy"; there are a lot of '
        'kinds of sexy - raunchy, dirty, flirty, coy, seductive, etc.'),
    'introduction_text': (
        'Please tell us anything you would like included '
        'in your introduction. You can do anything from provide us with '
        'basic information that the host will incorporate into your '
        'introduction to write an introduction you would like read exactly '
        'as is.'),
    'crew_instruct': (
        'Please use this space to clarify anything from the five checkboxes '
        'above'),
    'props_during': (
        'If our crew needs to hand you something or help you, please explain'
        ' and give a specific indication of when they should do it.'),
    'remove': (
        'Items to be removed after the act is complete, please include an '
        'inventory of costume items.'),
    'start_blackout': (
        'All lighting will black out to give you time to get '
        'into a position, lighting will come up at the same time as the '
        'audio.'),
    'end_blackout': ('All lighting will black out as soon as the music stops, '
                     'allowing you to exit in darkness.')}

starting_position_choices = [
    ('Onstage', 'Onstage'),
    ('In the wings', 'In the wings'),
    ('In the house', 'In the house')
]

bidder_info_phone_error = ('A phone number we can use to reach you '
                           ' when you are at the Expo, such as cell phone.')

act_length_required = ("Act Length (mm:ss) is required.")
act_length_too_long = ("The Act Length is too long.")

act_help_texts = {
    'shows_preferences': 'Check as many as apply to you',
    'act_duration': ('Length of entire act in mm:ss - please include any time '
                     'you are performing before or after your song.'),
    'track_duration': ('Please enter the duration of your music or backing '
                       'track in minutes and seconds. Something that was four '
                       'minutes and twenty seconds would be entered as '
                       '"04:20". Remember, the maximum duration for an act in '
                       'competition in The Main Event is 5 minutes for a '
                       'soloist, 7 minutes for a group'),
    'description': ('Please give a brief description of your act. Stage '
                    'kittens will retrieve costumes and props, but we cannot '
                    'clean the stage after your act. Please do not leave '
                    'anything on the stage (water, glitter, confetti, etc.)'),
    'performer': ('Select the stage persona or troupe who will be performing.'
                  ' Hit "create" to create a new persona or troupe.'),
    'other_performance': ("Don't feel badly if you're not accepted to perform "
                          "in one of the formal shows. We have a ton of other "
                          "ways to get your performance fix! Indicating that "
                          "you are interested in doing one or more of these "
                          "activities has no effect on whether or not you are "
                          "accepted to perform in a show. You may be accepted "
                          "to perform and still do these activities."),
    'video_link': 'Make sure to include \'http://\' ',
    'intro_text': 'This text will be used by the MC to introduce your act.',
    'notes': ('Please clarify any instructions with respect to prop setting, '
              'clearing, or cueing')
}

summer_help_texts = {
    'shows_preferences': 'Check as many as apply to you',
    'act_duration': (
        'Length of entire act in mm:ss - please include any time you are '
        'performing before or after your song.  There is no maximum length '
        'for acts, but remember we are trying to accommodate as many '
        'performers as possible. The longer the act, the more stringent '
        'the selection criteria'),
    'track_duration': (
        'Please enter the duration of your music or backing track in minutes '
        'and seconds.  Something that was four minutes and twenty seconds '
        'would be entered as "04:20".'),
}

act_bid_labels = {
    'performer': 'Performer',
    'b_title': 'Name of Act',
    'summer_shows_preferences': 'I am available to perform on',
    'shows_preferences': 'I am interested in',
    'other_performance': 'Other performance opportunities',
    'song_title': ' Name of Song',
    'song_artist': 'Song Artist',
    'track_duration': 'Duration of Song',
    'act_duration': 'Duration of Act',
    'description': 'Description of Act',
    'b_description': 'Description of Act',
    'video_choice': 'Video Notes',
    'why_you': ('Why Would You Like to Perform at The Great Burlesque '
                'Exposition?'),
    'video_link': 'URL of Video'
}
summer_bid_label = "I am available to perform on"

bio_required = "Performer/Troupe history is required."
bio_too_long = "The History is too long."
bio_help_text = 'Please give a brief performer/troupe history.'

act_description_required = "Description of the Act is required."
act_description_too_long = "The Description  is too long."

promo_required = "Please provide a photo."
promo_help_text = ('Please_upload a photograph of yourself (photo must '
                   'be under 10 MB).')

persona_labels = {'name': ('Stage Name'),
                  'homepage': ('Web Site'),
                  'contact': ('Agent/Contact'),
                  'bio': ('Bio'),
                  'experience': ('Experience'),
                  'awards': ('Awards'),
                  'promo_image': ('Promo Image'),
                  'puffsheet': ('Press kit/one-sheet'),
                  'festivals': ('Festival Appearances and Honors'),
                  }


persona_help_texts = {
    'name': 'This is the name you will be listed under when performing.',
    'contact': ('The person GBE should contact about Expo  performances. \
        Usually, this will be you.'),
    'homepage': 'This will be listed on your performer page.',
    'bio': 'This will be listed on your performer page.',
    'promo_image': ('This may be used by GBE for promotional purposes, and '
                    'will appear on your performer page.'),
    'puffsheet': ("If you have a one-sheet or other prepared presskit, you "
                  "may upload it, and we'll include it in your promo page. "),
    'experience': 'Number of years performing burlesque',
    'awards': ('Other awards and recognition of your work in burlesque, '
               'including festival appearances not listed above.'),
    'festivals': ('If you have appeared in any of these festivals, let '
                  'us know how you did. This information will appear on '
                  'your performer page.'),
}

bid_review_options = ('Accepted', 'Declined', 'Waitlist')

acceptance_labels = {
    'accepted': ('Change Bid State')
}

acceptance_help_texts = {
    'accepted': ('Accept - will show the item on public pages as part of GBE, \
        Accept or Reject - will show up on the bidder\'s home page'),
    'level': ('Featured vendors show up with a larger Fashion Fair display, \
        and are positioned at the top of the page')
}


actbid_error_messages = {
    'b_title': {
        'required': ("The Title is required."),
        'max_length': ("The title of the act is too long."),
    }}

actbid_name_missing = ['...a name is needed']
actbid_otherperformers_missing = ['...please describe the other performers.']
actbid_group_wrong = ['If this is a group... other entries are needed.']
actbid_group_error = '''The submission says this is a group act, but there are \
no other performers listed'''

video_error1 = ['Either say that no video is provided.']
video_error2 = ['... or provide video']
video_error3 = '''The Video Description suggests a Video Link would be provided, \
but none was provided.'''

description_required = ("Description is required.")
description_too_long = ("The Description is too long.")
description_help_text = '''For use on the The Great Burlesque Expo website, \
    in advertising and in any schedule of events. The description should be \
    1-2 paragraphs.'''

avoided_constraints_popup_text = '''<strong>Info!</strong>
    We will do our best to accommodate everyone's requests when scheduling
    classes, but please realize that is not always possible. The more to
    flexible you can be, the more likely we are to be able schedule your
    class. Thanks for your understanding!'''

summer_act_popup_text = '''<strong>Instructions (please read!):
    </strong> Thanks for submitting an act for consideration at the Summer
    2017 MiniBurlExpo. As long as you have completed all of the bold fields,
    you will be able to save this form as a draft and come back and edit it.
    Once you are happy with it, pay your application fee, wait a few moments,
    and come back here to submit this act by pressing the Submit button at
    the bottom of the page.<br><br>
    The MiniBurlExpo is a new venture for us. We don't know how many shows
    we're having or even how many nights of shows. Please let us know all
    nights that you would be able to be in town and perform. The current
    plans is to have one show on Saturday night and classes during the day.
    If there is demand, we?ll add a second show on Saturday, and then a
    show on Friday, and then a show on Sunday.'''

classbid_labels = {
    'min_size': ('Minimum Size'),
    'maximum_enrollment': ('Maximum Students'),
    'history': ('Have You Taught This Class Before?'),
    'other_teachers': ('Fellow Teachers'),
    'run_before': 'Has the Class been run Before?',
    'fee': 'Materials Fee',
    'space_needs': 'Room Preferences',
    'schedule_constraints': 'Preferred Teaching Times',
    'avoided_constraints': 'I Would Prefer to Avoid',
    'multiple_run': 'Are you willing to run the class more than once?',
    'length_minutes': ('Length in Minutes'),
    'b_title': 'Title',
    'b_description': 'Description',
    'e_title': 'Title',
    'e_description': 'Description',
}

classdisplay_labels = {
    'type': ('Class Type'),
    'fee': ('Materials Fee (paid to teacher)'),
    'history': ('Have You Taught This Class Before?'),
    'other_teachers': ('Fellow Teachers'),
    'run_before': 'Has the Class been run Before?',
    'fee': 'Materials Fee',
    'space_needs': 'Room Preferences',
    'schedule_constraints': 'Preferred Teaching Times',
    'avoided_constraints': 'I Would Prefer to Avoid',
    'multiple_run': 'Are you willing to run the class more than once?',
    'length_minutes': ('Length in Minutes'),
}

classbid_help_texts = {
    'min_size': ("The minimum number of people required for your class. "
                 "This guideline helps the convention meet both teacher "
                 "expectations and class size needs. If you're not sure, "
                 "make the minimum 1"),
    'max_size': ('The maximum number of people that the class can \
                 accomodate.'),
    'history': ('Have you taught this class before? Where and when?'),
    'run_before': ('If the class has been run before, please let us know '
                   'where and when.'),
    'fee': ('We strongly suggest that your materials fee not exceed $10'),
    'physical_restrictions': ('Physical Restrictions'),
    'schedule_constraints': ('Scheduling Constraints'),
    'avoided_constraints': ('Times You Prefer To Avoid'),
    'multiple_run': ('Are you willing to run the class more than once?'),
    'length_minutes': ('Please note that classes are asked to end 10 '
                       'minutes shorter than the full slot length, '
                       'so a 60 minute class is really 50 minutes.'),
        }
classbid_error_messages = {
    'length_minutes': {
        'required': ("Class Length (in minutes) is required."),
        'max_length': ("The Class Length is too long."),
    }}

class_schedule_options = [('0', 'Friday Afternoon'),
                          ('1', 'Saturday Morning'),
                          ('2', 'Saturday Afternoon'),
                          ('3', 'Sunday Morning'),
                          ('4', 'Sunday Afternoon')]

rank_interest_options = [(0, '--------------'),
                         (1, 'Not interested'),
                         (2, 'Slightly interested'),
                         (3, 'Neither interested nor disinterested'),
                         (4, 'Somewhat interested'),
                         (5, 'Strongly interested')]

space_error1 = ('''A class of workshop type cannot have space choices.''')
space_type_error1 = ('''A workshop has seating in a ring around the room, \
    other options are not available.''')
space_error2 = ('''A class of movement type cannot have lecture space \
    choices.''')
space_type_error2 = ('''A movement class may have room preferences \
    listed for movement classes, but the chosen lecture style arrangement \
    is not an option.''')
space_error3 = ('''A class of lecture type cannot have movement space \
    choices.''')
space_type_error3 = ('''A lecture class may have room preferences listed \
    for lecture classes, but the chosen movement style arrangement is not an \
    option.''')

panel_labels = {
    'other_teachers': ('Recommended Panelists'),
    'run_before': 'Has the Panel been run Before?',
}

panel_help_texts = {
    'other_teachers': ('It is far more likely that your panel may be '
                       'run at The Great Burlesque Expo if we can find '
                       'qualified panelists and a moderator - let us '
                       'know if you have any recommendations.'),
    'run_before': ('The Great Burlesque Expo 2014 is looking for convention '
                   'content that is new and that have successfully presented '
                   'before, either at a convention, or elsewhere. If this '
                   'content has run before, please describe where and when.'),
}

vendor_description_help_text = ('Please describe your good or services in 250 '
                                'words or less. We will publish this text on '
                                'the website.')

vendor_labels = {
    'description': 'Description of Goods or Services',
    'b_title': 'Company or business name',
    'vend_time': ("I'd like to vend..."),
    'want_help': ('Help Wanted'),
    'help_times': ("I'd like someone to help me... (Check All That Apply)"),
    'help_description': ("Tell Us About the Person You'd Like to Hire "),
    'website': 'Company website',
    'physical_address': 'Business Address',
    'publish_physical_address': 'Publish my business address',
    'upload_img': 'Logo',
}

vendor_help_texts = {
    'vend_time':  ('I\'d like to vend...'),
    'want_help': ('''Would you like us to help you find someone to work at \
    your booth or table with you?'''),
    'upload_img': ('''Please provide any logo you would like displayed on our \
    website and advertising'''),
    'description': ('''The information you enter here will be displayed \
    on the website exactly as you enter it, so please double-check it before \
    hitting submit'''),
    'physical_address': ('''If your business address is different from \
    the address you used when you registered for the website, please enter \
    your business address here.'''),

    'help_description': ('''The Great Burlesque Exposition can help you \
    find people to work for you. Please use this field to describe what sort \
    of work you want done (booth staff, models, hand out flyers, set-up or \
    teardown staff) and any requirements (for example, "must be able to lift \
    40 pounds", "must be knowledgeable about corsets", "must be able to drive \
    a standard").'''),
}

vendor_schedule_options = [('VSH0', 'Saturday, 9am to noon'),
                           ('VSH1', 'Saturday, 12pm to 4pm'),
                           ('VSH2', 'Saturday, 4pm to 8pm'),
                           ('VSH3', 'Saturday after 8pm'),
                           ('VSH4', 'Sunday, 9am to noon'),
                           ('VSH5', 'Sunday, 12pm to 4pm'),
                           ('VSH6', 'Sunday, 4pm to 8pm'),
                           ('VSH7', 'Sunday after 8pm')]
vendor_featured_options = [('Featured', 'Featured')]

help_time_choices = (('Saturday, 9am to noon', 'Saturday, 9am to noon'),
                     ('Saturday, 12pm to 4pm', 'Saturday, 12p to 4pm'),
                     ('Saturday, 4pm to 8pm', 'Saturday, 4pm to 8pm'),
                     ('Saturday after 8pm', 'Saturday after 8pm'),
                     ('Sunday, 9am to noon', 'Sunday, 9am to noon'),
                     ('Sunday, 12pm to 4pm', 'Sunday, 12p to 4pm'),
                     ('Sunday, 4pm to 8pm', 'Sunday, 4pm to 8pm'),
                     ('Sunday after 8pm', 'Sunday after 8pm'))

#  Would like to be able to insert this into the class proposal form
#  from upstream

class_proposal_form_text = {
    'header': ("Thanks for your interest in the Great Burlesque Expo. "
               "Suggestions are welcome for classes you'd like to see "
               "offered. Name and email address are optional: fill in if "
               "you'd like updates about classes and panels at the next Expo.")
}

class_proposal_help_texts = {
    'name': ("If you'd like to get updates about classes and panels at the "
             "Expo, fill in your email address."),
    'b_title': 'Your suggested title for this class or panel',
    'proposal': ('What does this class look like in your mind? Consider '
                 'telling us about material to cover, target audience, etc.'),
    'type': ('Is this a class (a lecture or workshop with a single teacher) '
             'or a panel (a less formal discussion with multiple '
             'participants)?')
}

class_proposal_labels = {
    'b_title': 'Name of Class',
    'name': 'Your Contact Info',
    'proposal': 'Class Description',
    'type': 'Type of Class'
}

proposal_edit_help_texts = {
    'name': 'Name or email of submitter',
    'title': 'This will be published in the presenter opportunity page',
    'proposal': 'Description for what the Expo would like to offer.',
    'type': ('Class, panel or either one would be OK.  If "either" '
             '- volunteers will be able to choose to be a teacher, '
             'moderator, or presenter'),
    'display': ('When this is checked, the item will appear on '
                'the "Volunteer to Present" page.')

}

proposal_edit_labels = {
    'title': 'Name of Class',
    'name': 'Submitter Info',
    'proposal': 'Description',
    'type': 'Type of Class/Panel',
    'display': 'Solicit Presenters?'
}

presenter_help_text = {
    'volunteering': 'Are you interested in volunteering for this opportunity?',
    'presenter': 'Please provide a background we can use for you as a \
                  presenter.',
    'bid': '',
    'how_volunteer': 'What role would you prefer?',
    'qualification': 'Please describe any qualities that make you particualrly \
                      great for this opportunity.'
}

ticket_item_labels = {
    'ticket_id': 'Ticket Item Id:',
    'live': 'Display Item to Users?:',
    'cost': 'Ticket Price:',
    'bpt_event': 'Event in BPT',
    'is_minimum': 'Act as minimum donation',
    'has_coupon': 'Coupon Required',
}
ticket_item_help_text = {
    'ticket_id': 'If using BPT, this must match the BPT configuration to sync. \
    if using PayPal, this is used for tracking only.',
    'live': 'Will be shown on this site, if it is within the start/end time',
    'bpt_event': 'Ticket collection - all tickets within this event count the \
    same.',
    'is_minimum': 'A donation supercedes any other ticket.  The lowest cost \
    among all tickets is the minimum.',
    'has_coupon': 'Coupon Required, only works with BPT, not available with \
    PayPal.  Anything with a cooupon is not shown in this site.',
    'start_time': 'When the event becomes available & is shown on site',
    'end_time': 'When the event is no longer available & is not shown on site',
    'add_on': 'Does not consitute a qualifying purchase for what the event \
    gives the user, it is an additional feature after a main purchase',
}
link_event_labels = {
    'bpt_events': "Choose from existing tickets",
    'bpt_event_id': "New BPT Event Id",
    'display_icon': "Display Icon"
}
link_event_help_text = {
    'display_icon': '''What is shown on the 'I Want to Buy Tickets'
        page.  Description is not shown there, it's pulled from BPT but not
        shown.  Display Icon must come from http://simplelineicons.com/
        -- NOTE:  Avoid the "."'''
}
bpt_event_labels = {
    'act_submission_event': 'Act Submission Fee?:',
    'vendor_submission_event': 'Vendor Submission Fee?:',
    'linked_events': 'GBE Events on Ticket:',
    'include_conference': 'Includes the Conference?:',
    'include_most': 'Whole Shebang?:',
    'badgeable': 'Print a Badge?:',
    'ticket_style': 'Other Ticket Notes:',
    'bpt_event_id': '(BPT) Event Id',
}

bpt_event_help_text = {
    'bpt_event_id': 'Must match the event if using BPT.  If using PayPal, \
    this value is irrelevant, but required.',
    'act_submission_event': 'Used to submit Act Applications',
    'vendor_submission_event': 'Used to submit Vendor Applications',
    'linked_events': ('Conference Items and Volunteer Opportunties are not in '
                      'this list.'),
    'include_conference': 'All Classes, Panels and Workshops are included.',
    'include_most': ('Everything except Master Classes and Volunteer '
                     'Opportunities'),
    'badgeable': 'The Reg Desk will print a name badge if this is true',
    'ticket_style': 'Special instructions for Reg Desk'
}

donation_labels = {'donation': 'Fee (pay what you will)'}
donation_help_text = {'donation': '''Our fee is set to the minimum shown \
here, but you may choose to pay more.'''}

username_label = 'Login'
username_help = ("Required. 30 characters or fewer. Letters, digits and "
                 "@ . + - _ only.")

conference_participation_types = [('Teacher', 'Teacher'),
                                  ('Moderator', 'Moderator'),
                                  ('Panelist', 'Panelist'),
                                  ('Any of the Above', 'Any of the Above')]

panel_participation_types = [('Moderator', 'Moderator'),
                             ('Panelist', 'Panelist'),
                             ('Any of the Above', 'Any of the Above')]

class_participation_types = [('Teacher', 'Teacher')]

list_titles = {
    'class': '''Class Descriptions at GBE''',
    'panel': '''Panel Descriptions at GBE''',
    'show': '''Shows at GBE''',
    'all': '''All Events''',
    'volunteer': '''Volunteer Opportunities''',
    'master': '''Master Classes''',
    'drop-in': '''Dropin Classes''',
    'special': '''Special Events'''
}

list_text = {
    'class': '''    <p> \
        The Conference at <b></b>The Great Burlesque Exposition</b> \
        features more than 60 hours of \
        class time over threee days.  It is the original Professional \
        Development Conference for \
        burlesque performers, founded on the philosophy that "If we don't \
        take ourselves seriously, \
        no one else will either". \
        </p> \
        <p> \
        Whether you're looking to boost a skill set to the next level \
        or develop some new skills, \
        The Conference has something for you from costuming to publicity to \
        philosophical \
        discussions.   \
        </p>''',
    'panel': '''    <p> \
        Panels are an opportunity for members of the burlesque community to \
        learn from one another and \
        share with one another in a semi-structured setting.  Less \
        goal-oriented than our classes and \
        workshops, panels are guided discussions between knowledgable \
        attendees.  Led by a moderator, \
        panels actively encourage feedback and dialogue between the "panel of \
        experts" and the attendees.\
        </p><p>Sitting on a panel is a great way to gain experience as a \
        public speaker or to see if you
        might want to teach a class some day.  You don't need to be an \
        expert to sit on a panel; you \
        just need to be excited and enthusiastic about the topic!</p><p>
        If you're interested in being a panelist, let ust know - sign up at I \
        want to... Be a Presenter</p> ''',
    'show': '''    <p> \
        Each year, The Great Burlesque Exposition searches the globe to bring \
        you the finest performers.  \
        We have four big shows on three big nights! \
        </p> ''',
    'all': '''    <p> \
        Check out the full list of all shows, classes, master classes, dropin \
        classes and special events!\
        </p> ''',
    'volunteer': '''    <p> \
        Check out the many ways you can help to make the expo even more \
        awesome!  We're always adding new ways to help, so check here often! \
        </p>''',
    'master': '''    <p> For the student of burlesque who wants to get even \
        more out of the conference, The Great Burlesque Exposition offers \
        Master Classes.  These are intensive, double-length classes \
        taught by world-renowned experts in burlesque.  If you want to take \
        your performance to the next level, this is how to do it. </p> <font \
        color="red">Please note:</font><br><br><ul><li>It is strongly \
        suggested you sign up for Master Classes in advance.  Space is
        limited and we expect them to sell out.</li>\
        <li>You do not need to be registered for any other portion of The \
        Great Burlesque Exposition to attend a Master Class.</li>\
        <li>Master Classes are not included in the Whole Shebang package.  \
        If you wish to attend a master \
        class, an additional fee applies.</li>''',
    'drop-in': '''    <p> Brought to you by the \
        <a href="http://www.studyburlesque.com">Boston Academy of Burlesque \
        Education (B.A.B.E.)</a> these classes are a great "tease" into the \
        art of Burlesque.</p> ''',
    'special': '''    <p> A collection of events so special that we had no \
        choice but to call them "Special Events".</p> '''
}

acceptance_note = '''Only accepted classes will show up in scheduling and on \
        the website.'''

# stop gap for refactoring - BB 4/28/2017
scheduling_help_texts = {
    'description': "Note, this will change the description for all bookings \
        of this event",
    'title': "Note, this will change the title for all bookings of this event",
    'e_description': "Note, this will change the description for all bookings \
        of this event",
    'e_title': "Note, this will change the title for all bookings of this \
        event",
    'duration': "Enter duration as HH:MM:SS"
}

scheduling_labels = {
    'e_title': 'Title',
    'e_description': 'Description',
}
schedule_occurrence_labels = {
    'duration': 'Duration (Hours)',
}
costume_proposal_form_text = '''<p>Thanks for your interest in our costume \
    display. Each year a team of creative volunteers puts together a \
    remarkable collection of burlesque costumes in our Exhibit Hall. The core \
    of the team are BettySioux Tailor and Blitzen vonSchtupp, with the \
    curatorial assistance of Miss Mina Murray.</p>\
    <p>Costumes are selected for their historical significance, their 'wow' \
    factor, their individuality (that is, we're not likely to take two \
    similar costumes or more than one costume from the same person), and \
    their craftsmanship. Not all costumes that are offered are accepted. \
    You can check on the status of your submission on your personal \
    homepage.</p>\
    <p>If you are offering a costume for display, it is your responsibility \
    to make sure that the costume is on-site before 9:00am on Saturday
    morning. Dropping it off on Friday is fine. If you drop it off before \
    6:00pm on Friday, it is likely it will be on display during The \
    Bordello. Costumes will be available for pick-up after 9:00pm on \
    Sunday evening. It is your responsibility to pick up your costume \
    and make sure all pieces are retrieved when you do so. In rare cases \
    and with previous arrangements, a costume can be picked up earlier on \
    Sunday or shipped to you after The Expo.</p>\
    <p>If you have questions about The Costume Display, please drop a \
    note to BettySioux Tailor at \
    <a href="mailto:Costumes@Burlesque-Expo.com">\
    Costumes@Burlesque-Expo.com</a>. If you'd like to be one of the \
    volunteers who puts up the display or one of the docents who helps \
    educate people about the costumes over the weekend, please check our \
    Volunteer Opportunities. '''

costume_proposal_help_texts = {
    'b_title': '''A unique way to identify the costume so we all know which \
        costume we're talking about.  You could use the name of the act it's \
        from, the material and color, or really anything so you know which \
        costume we're talking about.  We'll contact you about what you want \
        to call it on the exhibit text, if we have questions.''',
    'creator': '''Please put the stage name, legal name, or company name of \
        the creator, whichever is appropriate. If multiple creators, please \
        separate them with a comma. If unknown, just put 'unknown'.''',
    'act_title': 'The name of the act for which you use the costume, if any.',
    'debut_date': '''Please enter the month and year the costume first \
        appeared on-stage as "MM/YYYY" if known. If unknown, just put \
        'unknown'.''',
    'dress_size': 'Measurements are in USA dress sizes. A close approximation \
        is fine. This is to help us select which mannequin to use.',
    'picture': 'Please upload a portrait-oriented (taller than wide) image of \
        the costume that shows it to best advantage. This can either be in \
        performance or displayed on a mannequin or model.'
}

costume_proposal_labels = {
    'b_title': 'Name of Costume',
    'performer': 'Stage Name',
    'creator': 'Costume Creator',
    'act_title': 'Name of Act',
    'debut_date': 'Debut Date',
    'active_use': 'Is the costume still being used on-stage?',
    'pieces': 'How many pieces are there?',
    'description': 'Please list all pieces',
    'pasties': 'Will you be bringing pasties?',
    'dress_size': 'Dress Size',
    'more_info': 'Is there anything special about the costume you want us to \
        know?',
    'picture':  'Picture of the costume'
}

valid_model_error = '''Select a valid choice. That choice is not one of the \
    available choices.'''

theme_help = {
    'no_args': '''This form requires either an instance of a StyleValue or a
    StyleProperty from which to create the StyleValue so that the value type
    can be determined.''',
    'mismatch': '''The template of the property does not match the value.
    This suggests that something has changed since the value was last saved.'''
}
style_value_help = {
    'text-shadow-0': '''The position of the horizontal shadow.
    Negative values are allowed''',
    'text-shadow-1': '''The position of the vertical shadow.
    Negative values are allowed''',
    'text-shadow-2': '''The blur radius. Default value is 0''',
    'text-shadow-3': '''The color of the shadow.''',
    'box-shadow-0': '''The horizontal offset of the shadow. A positive value
    puts the shadow on the right side of the box, a negative value puts the
    shadow on the left side of the box''',
    'box-shadow-1': '''The vertical offset of the shadow. A positive value
    puts the shadow below the box, a negative value puts the shadow above
    the box''',
    'box-shadow-2': '''The blur radius. The higher the number, the more
    blurred the shadow will be''',
    'box-shadow-3': '''The spread radius. A positive value increases the size
    of the shadow, a negative value decreases the size of the shadow''',
    'box-shadow-4': '''The color of the shadow. The default value is the text
    color.'''}
