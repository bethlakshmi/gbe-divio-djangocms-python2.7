# literal text from gbe forms
# see gbetext.py for the rules
# until I copy them over

participant_labels = {
    'legal_first_name': ('Legal First Name'),
    'legal_last_name': ('Legal Last Name'),
    'display_name': ('Badge Name'),
    'best_time': ('Best time to call'),
    'how_heard': "How did you hear about The Expo?",
    'purchase_email': ('Ticket Purchase Email'),
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

# our event style setting had no canonical list.  This is not that list.
# Fix it, reuse it - Betty 2/18/23
event_styles_complete = [
    ('Drop-In', 'Drop-In Class'),
    ('Lecture', "Lecture"),
    ('Master', 'Master Class'),
    ('Movement', "Movement"),
    ('Panel', "Panel"),
    ('Rehearsal Slot', 'Rehearsal Slot'),
    ('Show', 'Show'),
    ('Special', 'Special Event'),
    ('Volunteer', 'Volunteering'),
    ('Workshop', "Workshop")]

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
        'roles': ['Producer', 'Technical Director', 'Stage Manager'],
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
    'Stage Manager': False,
}
all_roles = ["Scheduling Mavens", "Registrar"]
role_option_privs = {
    'Producer': ["Performer",
                 "Volunteer",
                 "Staff Lead",
                 "Stage Manager",
                 "Technical Director",
                 "Producer"],
    'Stage Manager': ["Performer",
                      "Volunteer",
                      "Staff Lead",
                      "Stage Manager",
                      "Technical Director",
                      "Producer"],
    'Technical Director': ["Performer",
                           "Volunteer",
                           "Staff Lead",
                           "Stage Manager",
                           "Technical Director",
                           "Producer"],
    'Act Coordinator': ["Performer",
                        "Technical Director",
                        "Stage Manager",
                        "Producer"],
    'Class Coordinator': ["Interested",
                          "Panelist",
                          "Teacher",
                          "Moderator"],
    'Volunteer Coordinator': ["Interested",
                              "Volunteer",
                              "Staff Lead",
                              "Stage Manager"],
    'Staff Lead': ["Volunteer", "Stage Manager", "Technical Director"]
}
event_collect_choices = [
                ("Conference", "All Conference Classes"),
                ("Drop-In", "All Drop-In Classes"),
                ("Volunteer", "All Volunteer Events")]
copy_mode_labels = {
    'copy_mode': "How would you like to copy this event?",
    'room': "Choose the default room",
    'solo_room': "Choose the room",
    'copy_mode_solo': "Options for how to copy the event",
}
copy_mode_choices = [
    ("copy_children_only",
     "Copy all sub-events to "),
    ("include_parent",
     "Include this event and all sub events, make new event on ")
]
copy_mode_solo_choices = [
    ("copy_to_parent",
     "Link to this parent event "),
    ("copy_to_area",
     "Link to this staff area "),
    ("choose_day",
     "Pick day - will be used instead of parent day if chosen")
]
copy_solo_mode_errors = {
    'required': 'Pick at least one of these options.',
}
copy_errors = {
    'room_conf_mismatch': "This room is not available for the conference on " +
    "this day.",
    'no_target': " Must choose the target event when copying sub-events.",
    'no_day': " Must choose a day when copying events.",
    'room_target_mismatch': "This room is not available for the conference " +
    "of the chosen event.",
    'no_area': "If this option is chosen, an area choice is required.",
    'no_delta': "Either a parent event, or a target date must be chosen.",
}
inform_about_options = [('Exhibiting Art or Costumes',
                         'Exhibiting Art or Costumes'),
                        ('Performing', 'Performing'),
                        ('Pre-event Organizing', 'Pre-event Organizing'),
                        ('Sponsoring/Advertising', 'Sponsoring/Advertising'),
                        ('Teaching', 'Teaching'),
                        ('Vending', 'Vending'),
                        ('Volunteering', 'Volunteering at the Expo')]
bidder_select_one = '''You must select at least one set of criteria - either
    the bidder (conference, statue and bid type) or the profile's interest'''
bid_state_required = "At least one bid state is required when emailing bidders"
bid_type_required = "At least one bid type is required when emailing bidders"
bid_conf_required = "At least one conference is required when emailing bidders"
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
    'phone': 'For the Expo only, in case we need to reach you.',
    'legal_name': ('We collect this for legal agreements like payments '
                   'or photo releases'),
}

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
    'type': '''Special Events, Master Classes, and Drop In classes are shown in
    event lists, Staff Areas do not.''',
    'slug': '''Short name for the event, this is displayed with any child
    events to show what they are a part of.'''}

available_time_conflict = \
    'Available times conflict with unavailable times.  Conflicts are: %s'

unavailable_time_conflict = \
    'Unavailable times conflict with Available times.'

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
    ('I have no props or set pieces',
     'I have no props or set pieces/my props enter & exit with me'),
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

act_help_texts = {
    'shows_preferences': 'Check as many as apply to you',
    'b_title': '''This will identify your act in all emails and with the
        crew.  If your act does not have a name, we suggest using the title
        of your song (track title).''',
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
                  ' Click "Add" to create a new individual or troupe bio, or'
                  ' "Edit" change the selected item.'),
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
              'clearing, or cueing'),
    'performer_names': '''Required for groups of 2 more more.  Names of all
    performers in this act.''',
}

act_bid_labels = {
    'performer': 'Performer',
    'b_title': 'Name of Act',
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
    'video_link': 'URL of Video',
    'num_performers': "Number of Performers",
}
persona_labels = {'name': ('Stage Name'),
                  'contact': ('Agent/Contact'),
                  'bio': ('Bio'),
                  'year_started': ('Started In'),
                  'awards': ('Awards'),
                  'pronouns': ('Preferred Pronouns'),
                  'promo_image': ('Promo Image'),
                  'puffsheet': ('Press kit/one-sheet'),
                  'festivals': ('Festival Appearances and Honors'),
                  }

troupe_labels = persona_labels.copy()
troupe_labels['name'] = ('Troupe Name')
troupe_labels['year_started'] = ('Started In')

pronoun_choices = [("she/her", "She/her"),
                   ("he/him", "He/him"),
                   ("they/them", "They/them"),
                   ("", "Other")]
persona_help_texts = {
    'name': 'This is the name you will be listed under when performing.',
    'label': '''Reminder for when you use this bio.  Helps to manage multiple
    bios.''',
    'contact': ('The person GBE should contact about Expo  performances. \
        Usually, this will be you.'),
    'bio': 'This will be listed on your performer page.',
    'promo_image': ('This may be used by GBE for promotional purposes, and '
                    'will appear on your performer page.'),
    'puffsheet': ("If you have a one-sheet or other prepared presskit, you "
                  "may upload it, and we'll include it in your promo page. "),
    'year_started': 'First year you performed or taught',
    'awards': ('Other awards and recognition of your work in burlesque, '
               'including festival appearances not listed above.'),
    'festivals': ('If you have appeared in any of these festivals, let '
                  'us know how you did. This information will appear on '
                  'your performer page.'),
}
article_help_texts = {
    'live_as_of': '''Date to start displaying the article.  This only used if
    publish is set to 'Available after "Publish Date"'.'''
}
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

actbid_otherperformers_missing = ['...please describe the other performers.']
actbid_group_wrong = ['If this is a group... other entries are needed.']
actbid_group_error = '''The submission says this is a group act, but there are \
no other performers listed'''

avoided_constraints_popup_text = '''<strong>Info!</strong>
    We will do our best to accommodate everyone's requests when scheduling
    classes, but please realize that is not always possible. The more to
    flexible you can be, the more likely we are to be able schedule your
    class. Thanks for your understanding!'''

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
}

classdisplay_labels = {
    'type': ('Class Type'),
    'fee': ('Materials Fee (paid to teacher)'),
    'history': ('Have You Taught This Class Before?'),
    'other_teachers': ('Fellow Teachers'),
    'run_before': 'Has the Class been run Before?',
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
# keys must line up with keys in gbetext difficulty_options
difficulty_default_text = {
    'Easy': '''An introductory level.  Good for folks in the first 1-3 years
    of burlesque, or newcomers to a given topic''',
    'Medium': '''Good for folks who have already been introduced to burlesque,
    or who have some familiarity with the topic or an adjacent skill''',
    'Hard': '''A challenging class - either physically or mentally (or both!).
    Even those who are familiar with the topic/skill should expect to learn
    something new''',
    }

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
    'ticketing_event': 'Fee/Event',
    'is_minimum': 'Act as minimum donation',
    'has_coupon': 'Coupon Required',
    'special_comp': 'Anytime Comp',
}
ticket_item_help_text = {
    'ticket_id': 'If using BPT, this must match the BPT configuration to sync. \
    if using PayPal, this is used for tracking only.',
    'live': 'Will be shown on this site, if it is within the start/end time',
    'ticketing_event': 'What this ticket pays for - application fee, vendor spot, \
    ticket for conference, show, special event, etc.',
    'is_minimum': 'A donation supercedes any other ticket.  The lowest cost \
    among all tickets is the minimum.',
    'has_coupon': 'Coupon Required, only works with BPT, not available with \
    PayPal.  Anything with a cooupon is not shown in this site.',
    'start_time': 'When the event becomes available & is shown on site',
    'end_time': 'When the event is no longer available & is not shown on site',
    'add_on': 'Does not consitute a qualifying purchase for what the event \
    gives the user, it is an additional feature after a main purchase',
    'special_comp': 'This comp will let the user use it, even after the \
    application deadline is closed.'
}
link_event_labels = {
    'ticketing_events': "Choose from existing tickets",
    'ticket_types': "Chose from Humanitix Ticket Types",
    'event_id': "Ticket Event Id",
    'display_icon': "Display Icon"
}
ticketing_event_labels = {
    'act_submission_event': 'Act Submission Fee?:',
    'vendor_submission_event': 'Vendor Submission Fee?:',
    'linked_events': 'GBE Events on Ticket:',
    'include_conference': 'Includes the Conference?:',
    'include_most': 'Whole Shebang?:',
    'ticket_style': 'Other Ticket Notes:',
    'event_id': 'Event Id',
    'source': 'Managed By',
}

ticketing_event_help_text = {
    'event_id': 'Must match the event if using BPT.  If using PayPal, \
    this value is irrelevant, but required.',
    'act_submission_event': 'Used to submit Act Applications',
    'vendor_submission_event': 'Used to submit Vendor Applications',
    'linked_events': ('Conference Items and Volunteer Opportunties are not in '
                      'this list.'),
    'include_conference': 'All Classes, Panels and Workshops are included.',
    'include_most': ('Everything except Master Classes and Volunteer '
                     'Opportunities'),
    'ticket_style': 'Special instructions for Reg Desk',
    'display_icon': '''What is shown on the 'I Want to Buy Tickets'
        page.  Description is not shown there, it's pulled from BPT but not
        shown.  Display Icon must come from http://simplelineicons.com/
        https://icons.getbootstrap.com/ (version 1.10.2) or
        https://nagoshiashumari.github.io/Rpg-Awesome/
        -- NOTE:  use only the icon class, for example
        <i class="JUST USE THIS STUFF"></i>''',
    'slug': 'At present, the slug is only used for Humanitix tickets, as \
    part of the URL generation.'
}

donation_labels = {'donation': 'Fee (pay what you will)'}
donation_help_text = {'donation': '''Our fee is set to the minimum shown \
here, but you may choose to pay more.'''}
user_form_help = {
    'name': ('The name you would like to see on any badges, communication '
             'from this event, or public ways of referring to you.')
}

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
        The Conference at <b>The Great Burlesque Exposition</b> \
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
        class="gbe-form-error">Please note:</font><br><br><ul><li>It is \
        strongly suggested you sign up for Master Classes in advance.  Space
        is limited and we expect them to sell out.</li>\
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

theme_help = {
    'no_args': '''This form requires either an instance of a StyleValue or a
    StyleProperty from which to create the StyleValue so that the value type
    can be determined.''',
    'mismatch': '''The template of the property does not match the value.
    This suggests something has changed since the value was last saved.''',
    'bad_elem': '''The format of this style includes an unrecognized value.'''
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
    color.''',
    'change_images': '''Selecting or Uploading images will not remove images
    from the system.  Only images uploaded through this form are shown.''',
    'add_image': '''Uploading an image takes precedence over any selected
    image.''',
}
sender_name_help = ('The name of the sender.  Recipients will get email ' +
                    'from "Sender Name <From>')
event_search_guide = "You can search by title, event type or id (pk)"
resource_search_guide = '''You can search by name (of room), or id (pk) -
 pardon the mess, there is residue from old data that needs cleanup'''
