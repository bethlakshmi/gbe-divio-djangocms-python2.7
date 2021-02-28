from django.urls import reverse

special_menu_tree = [
    {'title': 'Contact',
     'url': '',
     'parent_id': 1,
     'id': 2,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Ticketing - Admin',
                'Registrar',
                'Staff Lead',
                'Technical Director',
                ]},
    {'title': 'Bidders By Email',
     'url': reverse('mail_to_bidders',
                    urlconf='gbe.email.urls'),
     'parent_id': 2,
     'id': 46,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Roles By Email',
     'url': reverse('mail_to_roles',
                    urlconf='gbe.email.urls'),
     'parent_id': 2,
     'id': 52,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Producer',
                'Registrar',
                'Schedule Mavens',
                'Staff Lead',
                'Technical Director',
                'Volunteer Coordinator',
                ]},
    {'title': 'Manage',
     'url': '',
     'parent_id': 1,
     'id': 10,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Registrar',
                'Staff Lead',
                'Scheduling Mavens',
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
                'Producer'
                ]},
    {'title': 'Most Reports',
     'url': reverse('reporting:report_list'),
     'parent_id': 20,
     'id': 49,
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
    {'title': 'Act Tech Reports',
     'url': reverse('reporting:act_techinfo_review'),
     'parent_id': 20,
     'id': 55,
     'groups': ['Scheduling Mavens',
                'Tech Crew',
                'Technical Director',
                'Producer']},
    {'title': 'Class Evaluations Report',
     'url': reverse('reporting:evaluation'),
     'parent_id': 20,
     'id': 50,
     'groups': ['Class Coordinator',
                ]},
    {'title': 'Class Interest Report',
     'url': reverse('reporting:interest'),
     'parent_id': 20,
     'id': 51,
     'groups': ['Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Print Schedules',
     'url': reverse('reporting:welcome_letter'),
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
    {'title': 'Volunteer Staffing Reports',
     'url': reverse('reporting:staff_area'),
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
                'Staff Lead',
                'Vendor Reviewers',
                'Vendor Coordinator',
                'Volunteer Reviewers',
                'Volunteer Coordinator',
                'Tech Crew']},
    {'title': 'Acts',
     'url': reverse('act_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 31,
     'groups': ['Act Reviewers',
                'Act Coordinator']},
    {'title': 'Act Tech Info',
     'url': reverse('act_techinfo_review', urlconf='gbe.reporting.urls'),
     'parent_id': 30,
     'id': 32,
     'groups': ['Tech Crew']},
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
    {'title': 'Proposals',
     'url': reverse('proposal_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 35,
     'groups': ['Class Coordinator']},
    {'title': 'Vendors',
     'url': reverse('vendor_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 36,
     'groups': ['Vendor Reviewers',
                'Vendor Coordinator']},
    {'title': 'Volunteers',
     'url': reverse('review_pending', urlconf='gbe.scheduling.urls'),
     'parent_id': 30,
     'id': 37,
     'groups': ['Volunteer Reviewers',
                'Volunteer Coordinator',
                'Staff Lead']},
    {'title': 'Schedule',
     'url': '',
     'parent_id': 1,
     'id': 40,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'All Events',
     'url': reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls'),
     'parent_id': 40,
     'id': 43,
     'groups': ['Scheduling Mavens']},
    {'title': 'Acts',
     'url': reverse('schedule_acts', urlconf='gbe.scheduling.urls'),
     'parent_id': 40,
     'id': 41,
     'groups': ['Act Coordinator',
                'Scheduling Mavens']},
    {'title': 'Conferences',
     'url': reverse('manage_conference',
                    urlconf='gbe.scheduling.urls'),
     'parent_id': 40,
     'id': 60,
     'groups': ['Scheduling Mavens']},
]
