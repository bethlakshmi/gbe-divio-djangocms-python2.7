from django.urls import reverse
from gbe.email.views import (
    MailToBiddersView,
    MailToPersonView,
    MailToRolesView,
)
from gbe.reporting.views import PerformerSlidesList


special_menu_tree = [
    {'title': 'Contact',
     'url': '',
     'parent_id': 1,
     'id': 2,
     'groups': MailToRolesView.reviewer_permissions + (
          MailToBiddersView.reviewer_permissions)},
    {'title': 'Bidders By Email',
     'url': reverse('mail_to_bidders',
                    urlconf='gbe.email.urls'),
     'parent_id': 2,
     'id': 46,
     'groups': MailToBiddersView.reviewer_permissions},
    {'title': 'Roles By Email',
     'url': reverse('mail_to_roles',
                    urlconf='gbe.email.urls'),
     'parent_id': 2,
     'id': 52,
     'groups': MailToRolesView.reviewer_permissions},
    {'title': 'Manage',
     'url': '',
     'parent_id': 1,
     'id': 10,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Producer',
                'Registrar',
                'Staff Lead',
                'Scheduling Mavens',
                'Stage Manager',
                'Technical Director',
                'Theme Editor',
                'Ticketing - Admin',
                'Ticketing - Transactions',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Email Templates',
     'url': reverse('list_template', urlconf='gbe.email.urls'),
     'parent_id': 10,
     'id': 45,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Registrar',
                'Scheduling Mavens',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'News Articles',
     'url': reverse('news_manage', urlconf="gbe.urls"),
     'parent_id': 10,
     'id': 48,
     'groups':  MailToPersonView.email_permissions + (
          MailToRolesView.reviewer_permissions) + (
          MailToBiddersView.reviewer_permissions)},
    {'title': 'Themes',
     'url': reverse('themes_list', urlconf='gbe.themes.urls'),
     'parent_id': 10,
     'id': 60,
     'groups': ['Theme Editor',
                ]},
    {'title': 'Tickets',
     'url': reverse('ticket_items', urlconf='ticketing.urls'),
     'parent_id': 10,
     'id': 11,
     'groups': ['Ticketing - Admin',
                ]},
    {'title': 'Ticket Transactions',
     'url': reverse('transactions', urlconf='ticketing.urls'),
     'parent_id': 10,
     'id': 12,
     'groups': ['Ticketing - Transactions',
                ]},
    {'title': 'Troupes',
     'url': reverse('manage_troupes', urlconf='gbe.urls'),
     'parent_id': 10,
     'id': 14,
     'groups': ['Act Coordinator',
                'Registrar',
                ]},
    {'title': 'Users',
     'url': reverse('manage_users', urlconf='gbe.urls'),
     'parent_id': 10,
     'id': 13,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Registrar',
                'Staff Lead',
                'Ticketing - Admin',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Report',
     'url': '',
     'parent_id': 1,
     'id': 20,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                'Technical Director',
                ] + PerformerSlidesList.view_perm,
     'admin_access': True},
    {'title': 'Badge Print Run (CSV)',
     'url': reverse('badge_print', urlconf="ticketing.urls"),
     'parent_id': 20,
     'id': 56,
     'groups': ['Registrar',
                ]},
    {'title': 'Class Evaluations Report',
     'url': reverse('evaluation', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 50,
     'groups': ['Class Coordinator',
                ]},
    {'title': 'Class Interest Report',
     'url': reverse('interest', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 51,
     'groups': ['Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Envelope Stuffing Report (CSV)',
     'url': reverse('env_stuff', urlconf="gbe.reporting.urls"),
     'parent_id': 20,
     'id': 552,
     'groups': ['Registrar',
                ]},
    {'title': 'Performer Comps',
     'url': reverse('perf_comp', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 57,
     'groups': ['Registrar',
                ]},
    {'title': 'Print Schedules',
     'url': reverse('welcome_letter', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 53,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Registration Checklist Setup',
     'url': reverse('checklistitem_list', urlconf="ticketing.urls"),
     'parent_id': 20,
     'id': 55,
     'groups': ['Ticketing - Admin', ]},
    {'title': 'Room Schedules',
     'url': reverse('room_schedule', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 550,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Room Setup',
     'url': reverse('room_setup', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 551,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Show Slides Data',
     'url': reverse('show_slide_list', urlconf="gbe.reporting.urls"),
     'parent_id': 20,
     'id': 59,
     'groups': PerformerSlidesList.view_perm},
    {'title': 'User Privileges',
     'url': reverse('user_privs', urlconf="gbe.reporting.urls"),
     'parent_id': 20,
     'id': 58,
     'groups': [],
     'admin_access': True},
    {'title': 'Volunteer Staffing Reports',
     'url': reverse('staff_area', urlconf='gbe.reporting.urls'),
     'parent_id': 20,
     'id': 54,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Review',
     'url': '',
     'parent_id': 1,
     'id': 30,
     'groups': ['Act Reviewers',
                'Act Coordinator',
                'Class Reviewers',
                'Class Coordinator',
                'Costume Reviewers',
                'Costume Coordinator',
                'Registrar',
                'Scheduling Mavens',
                'Staff Lead',
                'Tech Crew',
                'Ticketing - Admin',
                'Vendor Reviewers',
                'Vendor Coordinator',
                'Volunteer Reviewers',
                'Volunteer Coordinator']},
    {'title': 'Acts',
     'url': reverse('act_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 31,
     'groups': ['Act Reviewers',
                'Act Coordinator']},
    {'title': 'Classes',
     'url': reverse('class_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 33,
     'groups': ['Class Reviewers',
                'Class Coordinator']},
    {'title': 'Costumes',
     'url': reverse('costume_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 34,
     'groups': ['Costume Reviewers',
                'Costume Coordinator']},
    {'title': 'Vendors',
     'url': reverse('vendor_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 36,
     'groups': ['Vendor Reviewers',
                'Vendor Coordinator']},
    {'title': 'Approve Volunteers',
     'url': reverse('review_pending', urlconf='gbe.scheduling.urls'),
     'parent_id': 30,
     'id': 37,
     'groups': ['Volunteer Reviewers',
                'Volunteer Coordinator',
                'Staff Lead']},
    {'title': 'Review Volunteers',
     'url': reverse('volunteer_review', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 37,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Staff Lead',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Schedule',
     'url': '',
     'parent_id': 1,
     'id': 40,
     'groups': ['Admins',
                'Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'All Events',
     'url': reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls'),
     'parent_id': 40,
     'id': 43,
     'groups': ['Class Coordinator', 'Scheduling Mavens']},
    {'title': 'Expo Dates',
     'url': reverse('manage_conference',
                    urlconf='gbe.scheduling.urls'),
     'parent_id': 40,
     'id': 60,
     'groups': ['Admins']},
]
