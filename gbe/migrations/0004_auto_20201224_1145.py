# Generated by Django 3.0.11 on 2020-12-24 11:45
from django.db import migrations


init_values = [
    {
            'selector': '.gbe-header-band',
            'pseudo_class': '',
            'description': '''Boldly colored header bands with contrasting 
            text, such as above performer grids''',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('background-color', 'rgba(150,3,32,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': 'body.gbe-body',
            'pseudo_class': '',
            'description': 'Body of the page, except printable pages',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(255,255,255,1)'),
                         ('color', 'rgba(51,51,51,1)')]},
    {
            'selector': 'body.gbe-printable',
            'pseudo_class': '',
            'description': 'Body of the page, when it is printable',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(255,255,255,1)'),
                         ('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-alert-danger',
            'pseudo_class': '',
            'description': 'Alerts that show up dynamically on Error',
            'target_element': 'div',
            'usage': 'Alerts',
            'prop_val': [('background-color', 'rgba(248,215,218,1)'),
                         ('border-color', 'rgba(245,198,203,1)'),
                         ('color', 'rgba(114,28,36,1)')]},
    {
            'selector': '.gbe-alert-info',
            'pseudo_class': '',
            'description': 'Alerts that show up dynamically as Information',
            'target_element': 'div',
            'usage': 'Alerts',
            'prop_val': [('background-color', 'rgba(209,236,241,1)'),
                         ('border-color', 'rgba(190,229,235,1)'),
                         ('color', 'rgba(12,84,96,1)')]},
    {
            'selector': '.gbe-alert-success',
            'pseudo_class': '',
            'description': 'Alerts that show up dynamically on Success',
            'target_element': 'div',
            'usage': 'Alerts',
            'prop_val': [('background-color', 'rgba(212,237,218,1)'),
                         ('border-color', 'rgba(195,230,203,1)'),
                         ('color', 'rgba(21,87,36,1)')]},
    {
            'selector': '.gbe-alert-warning',
            'pseudo_class': '',
            'description': 'Alerts that show up dynamically on Warning',
            'target_element': 'div',
            'usage': 'Alerts',
            'prop_val': [('background-color', 'rgba(255,243,205,1)'),
                         ('border-color', 'rgba(255,238,186,1)'),
                         ('color', 'rgba(133,100,4,1)')]},
    {
            'selector': '.gbe-btn-primary',
            'pseudo_class': 'hover',
            'description': 'Buttons do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(71,31,31,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gbe-btn-primary',
            'pseudo_class': '',
            'description': '''Buttons to do the main work flow but not the
            paypal button''',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(107,46,46,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gbe-btn-primary',
            'pseudo_class': 'focus',
            'description': 'Buttons do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('outline-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)'),
                         ('background-color', 'rgba(71,31,31,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),]},
    {
            'selector': '.gbe-btn-table',
            'pseudo_class': '',
            'description': '''Small buttons to do actions on table rows''',
            'target_element': 'a',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(0,0,0,.05)'),
                         ('border-color', 'rgba(0,0,0,.15)')]},
    {
            'selector': '.gbe-btn-table',
            'pseudo_class': 'hover',
            'description': '''Small buttons to do actions on table rows''',
            'target_element': 'a',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(0,0,0,.20)'),
                         ('border-color', 'rgba(0,0,0,.30)')]},
    {
            'selector': '.gbe-table-link',
            'pseudo_class': '',
            'description': '''Links in tables''',
            'target_element': 'a',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(0,123,255,1)'),
                         ('text-decoration-color', 'rgba(0,123,255,1)')]},
    {
            'selector': '.gbe-table-row td.approval_needed',
            'pseudo_class': '',
            'description': '''Cells where special handling is needed.''',
            'target_element': 'a',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(254,255,185,1)')]},
    {
            'selector': '#sub-table table tbody tr td',
            'pseudo_class': '',
            'description': '''Sub table within a table''',
            'target_element': 'td',
            'usage': 'Table',
            'prop_val': [('border-color', 'rgba(50,50,50,1)')]},
    {
            'selector': '.paypal-button form input',
            'pseudo_class': 'hover',
            'description': 'Buttons do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(71,31,31,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.paypal-button form input',
            'pseudo_class': '',
            'description': '''The paypal button on act/vendor payment is
            unusual - it's mostly an image, but what settings we can control
            are grouped with the other buttons.''',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(107,46,46,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.paypal-button form input',
            'pseudo_class': 'focus',
            'description': 'Buttons do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('outline-color', 'rgba(71,31,31,1)'),
                         ('color', 'rgba(255,255,255,1)'),
                         ('background-color', 'rgba(71,31,31,1)'),
                         ('border-color', 'rgba(71,31,31,1)'),]},
    {
            'selector': '.gbe-btn-secondary',
            'pseudo_class': 'hover',
            'description': 'Buttons that do not do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(149,120,123,1)'),
                         ('border-color', 'rgba(88,71,73,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gbe-btn-secondary.active',
            'pseudo_class': '',
            'description': 'Table columns when they are selected',
            'target_element': 'input',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(149,120,123,1)'),
                         ('border-color', 'rgba(88,71,73,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gbe-btn-secondary',
            'pseudo_class': '',
            'description': 'Buttons that do not do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(223,180,185,1)'),
                         ('border-color', 'rgba(149,120,123,1)'),
                         ('color', 'rgba(65,65,65,1)')]},
    {
            'selector': '.gbe-btn-secondary',
            'pseudo_class': 'focus',
            'description': 'Buttons that do not do the main work flow.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('outline-color', 'rgba(88,71,73,1)'),
                         ('color', 'rgba(255,255,255,1)'),
                         ('background-color', 'rgba(149,120,123,1)'),
                         ('border-color', 'rgba(88,71,73,1)')]},
    {
            'selector': 'input[type=search]',
            'pseudo_class': '',
            'description': 'Search Box on tables',
            'target_element': 'input',
            'usage': 'Table',
            'prop_val': [('outline-color', 'rgba(223,180,185,1)'),
                         ('color', 'rgba(0,0,0,1)'),
                         ('background-color', 'rgba(255,255,255,1)'),
                         ('border-color', 'rgba(200,200,200,1)')]},
    {
            'selector': '.gbe-btn-light',
            'pseudo_class': 'hover',
            'description': 'Hover for buttons that terminate the work',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(226,230,234,1)'),
                         ('border-color', 'rgba(226,230,234,1)'),
                         ('color', 'rgba(33,37,41,1)')]},
    {
            'selector': '.gbe-btn-light',
            'pseudo_class': '',
            'description': 'Buttons like cancel that interrupt work.',
            'target_element': 'input',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(248,249,250,1)'),
                         ('border-color', 'rgba(175,176,177,1)'),
                         ('color', 'rgba(33,37,41,1)')]},
    {
            'selector': '.gbe-form-error',
            'pseudo_class': '',
            'description': '''Text that informs user of a form error or a
            table with problem data.''',
            'target_element': 'font',
            'usage': 'General',
            'prop_val': [('color', 'rgba(255,0,0,1)')]},
    {
            'selector': '.gbe-form-required',
            'pseudo_class': '',
            'description': 'The * on required form fields',
            'target_element': 'font',
            'usage': 'Forms',
            'prop_val': [('color', 'rgba(255,0,0,1)')]},
    {
            'selector': '.helptext',
            'pseudo_class': '',
            'description': 'The * on required form fields',
            'target_element': 'font',
            'usage': 'Forms',
            'prop_val': [('color', 'rgba(128,128,128,1)')]},

    {
            'selector': '.gbe-table-success td',
            'pseudo_class': '',
            'description': 'Table row when it was just successfully updated',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(195,230,203,1)')]},
    {
            'selector': '.gbe-table-row.gbe-table-info td',
            'pseudo_class': '',
            'description': '''Table row when it's highlighted for important
            information''',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(217,237,247,1)')]},
    {
            'selector': '.gbe-table-row.gbe-table-danger td',
            'pseudo_class': '',
            'description': 'Table row with a concern, like an inactive user.',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(242,222,222,1)')]},
    {
            'selector': '.gbe-striped-table-danger td',
            'pseudo_class': '',
            'description': '''Table row with a concern on a striped table,
            it's darker to make it stick out better, should match
            "gbe-form-error"''',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(255,0,0,1)')]},
    {
            'selector': 'table thead tr.gbe-table-header th',
            'pseudo_class': '',
            'description': 'Header of tables',
            'target_element': 'tr',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(200,200,200,1)'),
                         ('border-color', 'rgba(50,50,50,1)'),
                         ('color', 'rgba(0,0,0,1)')]},
    {
            'selector': 'table thead tr.gbe-table-header th',
            'pseudo_class': 'hover',
            'description': 'Header of tables, when moused over',
            'target_element': 'tr',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(200,200,200,1)')]},
    {
            'selector': 'table tfoot tr.gbe-table-header th',
            'pseudo_class': '',
            'description': 'Footer of tables',
            'target_element': 'tr',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(200,200,200,1)'),
                         ('border-color', 'rgba(50,50,50,1)'),
                         ('color', 'rgba(0,0,0,1)')]},
    {
            'selector': 'table tfoot tr.gbe-table-header th',
            'pseudo_class': 'hover',
            'description': 'Footer of tables, when moused over',
            'target_element': 'tr',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(200,200,200,1)')]},
    {
            'selector': '.gbe-table-row td',
            'pseudo_class': '',
            'description': 'Non-header/footer rows',
            'target_element': 'tr',
            'usage': 'Table',
            'prop_val': [('background-color', 'rgba(255,255,255,1)'),
                         ('border-color', 'rgba(50,50,50,1)'),
                         ('color', 'rgba(0,0,0,1)')]},
    {
        'selector':
        'table.striped_table  tr.striped_table_row:nth-child(even)',
        'pseudo_class': '',
        'description': 'Alternately striped table rows',
        'target_element': 'tr',
        'usage': 'Table',
        'prop_val': [('background-color', 'rgba(204,204,204,1)')]},
    {
        'selector': 'table.striped_table  tr.striped_table_row:nth-child(odd)',
        'pseudo_class': '',
        'description': 'Alternately striped table rows (the other half_',
        'target_element': 'tr',
        'usage': 'Table',
        'prop_val': [('background-color', 'rgba(238,238,238,1)')]},
    {
        'selector':
        '.gbe-list-even',
        'pseudo_class': '',
        'description': '''Alternately striped rows, done via divs for
        moble friendliness''',
        'target_element': 'tr',
        'usage': 'Table',
        'prop_val': [('background-color', 'rgba(204,204,204,1)')]},
    {
        'selector': '.gbe-list-odd',
        'pseudo_class': '',
        'description': '''Alternately striped rows, done via divs for
        moble friendliness''',
        'target_element': 'tr',
        'usage': 'Table',
        'prop_val': [('background-color', 'rgba(238,238,238,1)')]},

    {
            'selector': '.border-table tbody tr td,.border-table tbody tr th',
            'pseudo_class': '',
            'description': 'border around striped table(s)',
            'target_element': 'table',
            'usage': 'Table',
            'prop_val': [('border-color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-text-success',
            'pseudo_class': '',
            'description': '''Text that means to show success, like icons for
            something that is live.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(35,145,60,1)')]},
    {
            'selector': '.gbe-text-muted',
            'pseudo_class': '',
            'description': '''Text that is possibly active, but muted to
            defer tp something else.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(108,117,125,1)')]},
    {
        'selector': '.gbe-text-secondary',
        'pseudo_class': '',
        'description': '''Text that should recede a bit, because it's
        secondary.''',
        'target_element': 'i',
        'usage': 'Table',
        'prop_val': [('color', 'rgba(108,117,125,1)')]},
    {
        'selector': '.gbe-text-warning',
        'pseudo_class': '',
        'description': '''Text that indicates warning, but not complete
        failure.''',
        'target_element': 'i',
        'usage': 'Table',
        'prop_val': [('color', 'rgba(255,193,7,1)')]},
    {
            'selector': '.gbe-text-danger',
            'pseudo_class': '',
            'description': '''Text that means danger - not exactly an error,
            but something permanent,like reject/delete.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(220,53,69,1)')]},
    {
            'selector': '.gbe-text-info',
            'pseudo_class': '',
            'description': '''Text that is highlighted because it gives useful
            information.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(23,162,184,1)')]},
    {
            'selector': '.link-events-plus',
            'pseudo_class': '',
            'description': '''Used for a plus sign that is an active link
            information.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(220,220,220,1)')]},
    {
            'selector': '.link-events-plus',
            'pseudo_class': 'hover',
            'description': '''Plus sign as active link when hovered on.''',
            'target_element': 'i',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-draft',
            'pseudo_class': '',
            'description': 'The * on required form fields',
            'target_element': 'font',
            'usage': 'Forms',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.sched_label',
            'pseudo_class': '',
            'description': 'labels for event details',
            'target_element': 'font',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gallery-item .icons i',
            'pseudo_class': '',
            'description': '''icons that show when one hovers over a
            performer image''',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gallery-item .icons i',
            'pseudo_class': 'hover',
            'description': '''icons that show when one hovers over a
            performer image and also hovers over the icon''',
            'target_element': 'i',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(233,30,99,1)'),
                         ('border-color', 'rgba(233,30,99,1)')]},
    {
            'selector': '#team .single-member',
            'pseudo_class': 'hover',
            'description': '''Block to put focus to featured items on a page,
            see it on fashion faire and shows with special guests.  On hover,
            the shadow gets a bit deeper,throwing more focus.''',
            'target_element': 'div',
            'usage': 'Event Display',
            'prop_val': [('box-shadow',
                          'px px px px rgba',
                          '0px 6px 15px 0px rgba(0,0,0,0.14)')]},
    {
            'selector': '#team .single-member',
            'pseudo_class': '',
            'description': '''Block to put focus to featured items on a page,
            see it on fashion faire and shows with special guests.''',
            'target_element': 'div',
            'usage': 'Event Display',
            'prop_val': [
                ('box-shadow',
                 'px px px px rgba',
                 '0px 1px 3px 0px rgba(0,0,0,0.2)'),
                ('background', 'rgba(255,255,255,1)')]},
    {
            'selector': '#team .team-img',
            'pseudo_class': 'before',
            'description': '''Shaded color that comes over the image of a 
            featured block when the buttons show up.  Used in both vendors,
            and shows.''',
            'target_element': 'div',
            'usage': 'Event Display',
            'prop_val': [('background', 'rgba(233,30,99,0.7)')]},
    {
            'selector': '.social-icon .social i',
            'pseudo_class': '',
            'description': '''Buttons on top of featured item images.  Appear
            on hover.''',
            'target_element': 'div',
            'usage': 'Event Display',
            'prop_val': [
                ('box-shadow',
                 'px px px px rgba',
                 '0px 2px 4px 0px rgba(0,0,0,0.2)'),
                ('color', 'rgba(119,119,119,1)'),
                ('background', 'rgba(255,255,255,1)')]},
    {
            'selector': 'span.dropt:hover span',
            'pseudo_class': 'hover',
            'description': 'The help text when it is triggerd by hover',
            'target_element': 'span',
            'usage': 'Forms',
            'prop_val': [('background', 'rgba(255,255,255,1)')]},
    {
            'selector': 'span.dropt span',
            'pseudo_class': '',
            'description': 'The help text border',
            'target_element': 'span',
            'usage': 'Forms',
            'prop_val': [('border-color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-bg-light',
            'pseudo_class': '',
            'description': '''lighter colored panels - sub panels within
            site, including update profile email options, review bids,
            view bids, event lists, and others.''',
            'target_element': 'div',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(248,249,250,1)'),
                         ('border-color', 'rgba(50,50,50,1)')]},
    {
            'selector': '.gbe-bg-dark',
            'pseudo_class': '',
            'description': '''darker colored panels - sub panels within
            site, including act tech info, and event time/date details.''',
            'target_element': 'div',
            'usage': 'Forms',
            'prop_val': [('background-color', 'rgba(195,189,191,1)'),
                         ('border-color', 'rgba(50,50,50,1)')]},
    {
            'selector': '.gbe-panel-list',
            'pseudo_class': '',
            'description': '''when the dark panels is used on a heading
            within a long list, the border gets very interruptive, so it's
            currently set to blend with the gbe-bg-dark backgroun.  If changed,
            look at class description list and bio list.''',
            'target_element': 'div',
            'usage': 'Forms',
            'prop_val': [('border-color', 'rgba(195,189,191,1)'),
                         ('background-color', 'rgba(0,0,0,0)')]},
    {
            'selector': '.gbe-panel-list div.card-header',
            'pseudo_class': '',
            'description': '''blend the bottom of the panel header''',
            'target_element': 'div',
            'usage': 'Forms',
            'prop_val': [('border-color', 'rgba(195,189,191,1)')]},
    {
            'selector': '.gbe-border-danger',
            'pseudo_class': '',
            'description': 'important outline to give focus on active panels',
            'target_element': 'div',
            'usage': 'Forms',
            'prop_val': [('border-color', 'rgba(220,53,69,1)')]},
    {
            'selector': '.login-button',
            'pseudo_class': '',
            'description': 'Login drop down button on nav bar.',
            'target_element': 'button',
            'usage': 'General',
            'prop_val': [('color', 'rgba(255,255,255,1)'),
                         ('background-color', 'rgba(107,46,46,1)'),
                         ('border-color', 'rgba(71,31,31,1)')]},
    {
            'selector': '.login-button',
            'pseudo_class': 'hover',
            'description': 'Login drop down button on nav bar, hover.',
            'target_element': 'button',
            'usage': 'General',
            'prop_val': [('color', 'rgba(211,211,211,1)')]},
    {
            'selector': '#login-dp,.gbe-form-dropdown',
            'pseudo_class': '',
            'description': '''Dropdowns with forms in them like login and
            theme cloning''',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('background-color', 'rgba(180,80,80)'),
                         ('color', 'rgba(33,37,41,1)')]},
    {
            'selector': '#login-dp a',
            'pseudo_class': '',
            'description': 'Links in the login dropdown',
            'target_element': 'a',
            'usage': 'General',
            'prop_val': [('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '#login-dp .bottom',
            'pseudo_class': '',
            'description': 'Bottom of the login box - box for new users',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('background-color', 'rgba(180,80,80)'),
                         ('border-top-color', 'rgba(221,221,221,1)'),
                         ('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '.gbe-navbar-default',
            'pseudo_class': '',
            'description': 'Navbar in default state - the not-active options',
            'target_element': 'div',
            'usage': 'Navbar',
            'prop_val': [('background-color', 'rgba(229,229,229,.49)'),
                         ('border-color', 'rgba(0,0,0,0)')]},
    {
            'selector': '#gbe_header_menu',
            'pseudo_class': 'hover',
            'description': 'Non-active text in navbar, on hoever.',
            'target_element': 'font',
            'usage': 'Navbar',
            'prop_val': [('color', 'rgba(175,21,21,1)'),
                         ('background-color', 'rgba(0,0,0,0)')]},
    {
            'selector': '#gbe_header_menu',
            'pseudo_class': '',
            'description': 'Non-active text in navbar, on hoever.',
            'target_element': 'font',
            'usage': 'Navbar',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.active #gbe_header_menu',
            'pseudo_class': '',
            'description': '''Currenty active navbar menu item, matches panel
            of content.''',
            'target_element': 'a',
            'usage': 'Navbar',
            'prop_val': [('background-color', 'rgba(235,235,235,1)'),
                         ('text-shadow',
                          'px px px rgba',
                          '0px 0px 8px rgba(255,0,51,1)')]},
    {
            'selector': '.shadow-highlight',
            'pseudo_class': '',
            'description': 'Used to highlight text that was/is being updated.',
            'target_element': 'span',
            'usage': 'Navbar',
            'prop_val': [('text-shadow',
                          'px px px rgba',
                          '0px 0px 8px rgba(255,0,51,1)')]},
    {
            'selector': '.gbe-dropdown-menu',
            'pseudo_class': '',
            'description': 'Dropdown navigational menu (any level)',
            'target_element': 'ul',
            'usage': 'Navbar',
            'prop_val': [('background-color', 'rgba(173,3,37,1)')]},
    {
            'selector': '#gbe_dropdown',
            'pseudo_class': '',
            'description': 'Dropdown menu text',
            'target_element': 'a',
            'usage': 'Navbar',
            'prop_val': [('color', 'rgba(255,255,255,1)')]},
    {
            'selector': '#gbe_dropdown',
            'pseudo_class': 'hover',
            'description': 'Dropdown menu text, on hover',
            'target_element': 'a',
            'usage': 'Navbar',
            'prop_val': [('color', 'rgba(233,250,163,1)'),
                         ('background-color', "rgba(0,0,0,1)")]},
    {
            'selector': '#gbe_dropdown',
            'pseudo_class': 'focus',
            'description': '''Dropdown menu text, on focus (selected but not
            currently moused over)''',
            'target_element': 'a',
            'usage': 'Navbar',
            'prop_val': [('color', 'rgba(233,250,163,1)'),
                         ('background-color', "rgba(0,0,0,1)")]},
    {
            'selector': '.gbe-panel',
            'pseudo_class': '',
            'description': '''top level panel on every page, all content is
            inside''',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('background-color', 'rgba(235,235,235,1)'),
                         ('border-color', 'rgba(221,221,221,1)')]},
    {
        'selector': '.gbe-tab-active,.gbe-tab-active:hover,.gbe-tab-area',
        'pseudo_class': '',
        'description': '''Background of the active tab and everything
        "on" it.''',
        'target_element': 'div',
        'usage': 'Table',
        'prop_val': [('background-color', 'rgba(221,221,221,1)')]},
    {
            'selector': '.gbe-tab-active,.gbe-tab-active:hover',
            'pseudo_class': '',
            'description': 'Text of the active tab',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(180,80,80,1)')]},
    {
            'selector': '.gbe-tab',
            'pseudo_class': '',
            'description': 'Text of the inactive tabs',
            'target_element': 'div',
            'usage': 'Table',
            'prop_val': [('color', 'rgba(150,150,150,1)')]},
    {
            'selector': '.gbe-tab:hover',
            'pseudo_class': '',
            'description': 'Inactive tabs on hover',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('color', 'rgba(150,150,150,1)'),
                         ('background-color', 'rgba(238,238,238,1)'),
                         ('border-color', 'rgba(238,238,238,1)')]},
    {
            'selector': '.gbe-title',
            'pseudo_class': '',
            'description': 'Main Title of every page',
            'target_element': 'h2',
            'usage': 'General',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-subtitle',
            'pseudo_class': '',
            'description': 'Secondary titles in any page',
            'target_element': 'h2',
            'usage': 'General',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-footer',
            'pseudo_class': '',
            'description': 'footer at bottom of every page',
            'target_element': 'div',
            'usage': 'General',
            'prop_val': [('color', 'rgba(255,255,255,1)'),
                         ('background-color', 'rgba(0,0,0,0)'),
                         ('border-color', 'rgba(0,0,0,0)')]},
    {
            'selector': '.gbe-modal-content',
            'pseudo_class': '',
            'description': 'Background of modal panes.',
            'target_element': 'div',
            'usage': 'Modal',
            'prop_val': [('color', 'rgba(0,0,0,1)'),
                         ('background-color', 'rgba(235,235,235,1)'),
                         ('border-color', 'rgba(0,0,0,.2)')]},
    {
            'selector': '.gbe-modal-header',
            'pseudo_class': '',
            'description': 'Header and footer of modal.',
            'target_element': 'div',
            'usage': 'Modal',
            'prop_val': [('color', 'rgba(0,0,0,1)'),
                         ('background-color', 'rgba(216,216,216,1)'),
                         ('border-color', 'rgba(229,229,229,1)')]},
    {
            'selector': '.gbe-link',
            'pseudo_class': '',
            'description': 'Links within modal panes.',
            'target_element': 'a',
            'usage': 'General',
            'prop_val': [('color', 'rgba(51,122,183,1)'),
                         ('text-decoration-color', 'rgba(51,122,183,1)')]},
    {
            'selector': '.bio_block',
            'pseudo_class': '',
            'description': 'box around bios on classes',
            'target_element': 'div',
            'usage': 'Event Display',
            'prop_val': [('border-color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-panel-link',
            'pseudo_class': '',
            'description': 'Links as headers of panels',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(51,51,51,1)'),
                         ('text-decoration-color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.gbe-panel-link',
            'pseudo_class': 'hover',
            'description': 'Links as headers of panels',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(51,51,51,1)'),
                         ('text-decoration-color', 'rgba(51,51,51,1)')]},
    {'selector': '.gbe-panel-table, .gbe-panel-table td, .gbe-panel-table th',
     'pseudo_class': '',
     'description': '''Tables embedded within panels - used in
     reporting.  Covers header, rows and border and is fairly subtle''',
     'target_element': 'table',
     'usage': 'Reporting',
     'prop_val': [('color', 'rgba(51,51,51,1)'),
                  ('border-top-color', 'rgba(221, 221, 221, 1)')]},
    {
            'selector': '.detail_link',
            'pseudo_class': '',
            'description': 'Icon for more information on events page',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(0,0,0,1)')]},
    {
            'selector': '.detail_link',
            'pseudo_class': 'hover',
            'description': 'Icon for more information on events page',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(110,110,110,1)')]},
    {
            'selector': '.detail_link',
            'pseudo_class': 'active',
            'description': 'Icon for more information on events page',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(110,110,110,1)')]},
    {
            'selector': ('.detail_link-disabled,.detail_link-disabled:hover, ' +
                ' .detail_link-disabled:active,.detail_link-disabled:visited'),
            'pseudo_class': '',
            'description': '''Detail link on events list that is disabled 
            because this user is not eligible''',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(195,189,191,1)')]},
    {
            'selector': ('.detail_link-detail_disable,.detail_link-detail_' +
                'disable:hover,.detail_link-detail_disable:active, ' +
                '.detail_link-detail_disable:visited'),
            'pseudo_class': '',
            'description': '''Detail link on event detail pages that is 
            disabled because user is not eligible.  Darker for dark panel.''',
            'target_element': 'a',
            'usage': 'Event Display',
            'prop_val': [('color', 'rgba(140,140,140,1)')]},
    {
            'selector': '.gbe-link',
            'pseudo_class': 'hover',
            'description': 'Links within modal panes - on hover',
            'target_element': 'a',
            'usage': 'General',
            'prop_val': [('color', 'rgba(35,82,124,1)'),
                         ('text-decoration-color', 'rgba(35,82,124,1)')]},
]


def initialize_style(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    StyleVersion = apps.get_model("gbe", "StyleVersion")
    StyleSelector = apps.get_model("gbe", "StyleSelector")
    StyleProperty = apps.get_model("gbe", "StyleProperty")
    StyleValue = apps.get_model("gbe", "StyleValue")
    version = StyleVersion(
        name="Baseline",
        number=1.0,
        currently_live=True,
        currently_test=True)
    version.save()

    for select_val in init_values:
        selector = StyleSelector(
            selector=select_val['selector'],
            description=select_val['description'],
            pseudo_class=select_val['pseudo_class'],
            target_element_usage=select_val['target_element'],
            used_for=select_val['usage'])
        selector.save()
        for prop_val in select_val['prop_val']:
            val = prop_val[1]
            if len(prop_val) == 2:
                style_prop = StyleProperty(
                    selector=selector,
                    style_property=prop_val[0],
                    value_type='rgba')
            elif len(prop_val) == 3:
                style_prop = StyleProperty(
                    selector=selector,
                    style_property=prop_val[0],
                    value_type=prop_val[1])
                val = prop_val[2]
            else:
                raise Exception("there should be 2 or 3 values here")
            style_prop.save()
            value = StyleValue(style_property=style_prop,
                               style_version=version,
                               value=val)
            value.save()


def destroy_style(apps, schema_editor):
    StyleVersion = apps.get_model("gbe", "StyleVersion")
    StyleSelector = apps.get_model("gbe", "StyleSelector")
    StyleVersion.objects.filter(name="Baseline", number=1.0).delete()
    for select_val in init_values:
        StyleSelector.objects.filter(
            selector=select_val['selector'],
            pseudo_class=select_val['pseudo_class']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0003_auto_20201224_0729'),
    ]

    operations = [
        migrations.RunPython(initialize_style, reverse_code=destroy_style),
    ]
