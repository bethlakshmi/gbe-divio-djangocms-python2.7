# Generated by Django 3.0.14 on 2021-08-02 07:16

from django.db import migrations
from django.urls import reverse


def initialize_style(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    StyleElement = apps.get_model("gbe", "StyleElement")
    StyleLabel = apps.get_model("gbe", "StyleLabel")
    TestURL = apps.get_model("gbe", "TestURL")
    StyleGroup = apps.get_model("gbe", "StyleGroup")
    StyleSelector = apps.get_model("gbe", "StyleSelector")
    StyleProperty = apps.get_model("gbe", "StyleProperty")
    StyleValue = apps.get_model("gbe", "StyleValue")

    # remove stuff we don't need for new look
    try:
        StyleProperty.objects.get(pk=25).delete()
        StyleProperty.objects.get(pk=26).delete()
        StyleProperty.objects.get(pk=27).delete()
        StyleProperty.objects.get(pk=31).delete()
        StyleProperty.objects.get(pk=32).delete()
        StyleProperty.objects.get(pk=33).delete()
        StyleProperty.objects.get(pk=34).delete()
    except:
        print("remember to repeat w pull from live")

    # properly initialize the values for the new logic
    for style_prop in StyleProperty.objects.all():
        template_string = ""
        for value_type_item in style_prop.value_type.split():
            if value_type_item == "rgba":
                template_string = template_string + "{} "
            elif value_type_item == "px":
                template_string = template_string + "{}px "
        style_prop.value_template = template_string.strip()
        style_prop.save()

    for value in StyleValue.objects.all():
        parseable = ""
        for item in value.value.split():
            if "px" in item:
                parseable = parseable + item.rstrip("px") + " "
            else:
                parseable = parseable + item + " "
        value.parseable_values = parseable.strip()
        value.save()

    url1 = TestURL(
        display_name="Personal Home Page",
        partial_url=reverse("home",  urlconf='gbe.urls'),
        test_notes=(
            "Unusual layout with various size buttons, " +
            "different color panels, and be sure to test in both laptop and" +
            " mobile app sizes (resize your browser window)."))
    url1.save()
    url2 = TestURL(
        display_name="Ticket Edit Page",
        partial_url="/ticketing/ticket_item_edit/277",
        test_notes=(
            "Has the 3 main button colors at the bottom of the form, and " + 
            "uses the calendar picker, which has some other button impacts."))
    url2.save()
    url3 = TestURL(
        display_name="Transaction Edit Page",
        partial_url="/ticketing/transactions",
        test_notes="The one place we show the disabled secondary button " +
        "(top of page")
    url3.save()
    url4 = TestURL(
        display_name="Manage Events Page (with Events)",
        partial_url="/scheduling/manage/GBE2018?GBE2018-calendar_type=0&" +
        "filter=Filter",
        test_notes="Shows tabs, filters, table icon buttons, and layers of " +
        "panels.")
    url4.save()
    url5 = TestURL(
        display_name="Public Ticket List",
        partial_url="/ticketing/",
        test_notes="The flashy page we show to users for ticket buying, it " +
        "has a bunch of unusual elements, including an bright button, " +
        "icons, and white panels for each ticket.")
    url5.save()
    group1 = StyleGroup(
        name="Buttons",
        test_notes="Be sure that button colors work on all panels, that text" +
        " is sharp and clear on the button, and that the respective colors " +
        "make sense on the page.",
        order=5)
    group1.save()
    group1.test_urls.add(url1)
    group1.test_urls.add(url2)
    group1.test_urls.add(url3)
    group1.test_urls.add(url4)
    group1.test_urls.add(url5)
    primary_button = StyleElement(
        name="Primary Button",
        group=group1,
        description="The main activity on any page.  This should stick out " +
        "the most, but can blend with the colors of the site.",
        order=5,
        sample_html='<a href="" class="btn gbe-btn-primary" role="button"' +
        '>Primary Button</a>')
    primary_button.save()
    secondary_button = StyleElement(
        name="Secondary Button",
        group=group1,
        description="The supporting activity on any page.  This should " +
        "rececede in comparison to the primary, but be more engaging than " +
        "cancel.",
        order=10,
        sample_html='<a href="" class="btn gbe-btn-secondary" role="button"' +
        '>Secondary Button</a>')
    secondary_button.save()
    disabled_button = StyleElement(
        name="Disabled Secondary Button",
        group=group1,
        description="A secondary button that is not active, usually a " +
        "toggle next to the active secondary button.",
        order=15,
        sample_html='<a class="btn gbe-btn-secondary-disabled disabled" ' +
        'href="" role="button">Disabled Button</a>')
    disabled_button.save()
    light_button = StyleElement(
        name="Light Button",
        group=group1,
        description="Light color in order to recede into the background." +
        "  Used for Cancel, but also for toggles and other low-key buttons.",
        order=20,
        sample_html='<a class="btn gbe-btn-light" href="" role="button">' +
        'Light Button</a>')
    light_button.save()
    buy_button = StyleElement(
        name="Ticket Buying Button",
        group=group1,
        description="Really bright button for a 'buy it now!' quality.  " +
        "Based on a template we liked, this is a bit different than other " +
        "pages",
        order=25,
        sample_html='<a href="" target="_blank" class="btn gbe-btn-common">' +
        'Buy It Button</a>')
    buy_button.save()
    background = StyleLabel(
        name="Background",
        group=group1,
        help_text="Main background of button, automatic shading is applied " +
        "on top.",
        order=5)
    background.save()
    border = StyleLabel(
        name="Border",
        group=group1,
        help_text="Border around top plane of button, should be a bit darker.",
        order=10)
    border.save()
    side = StyleLabel(
        name="Button Side",
        group=group1,
        help_text="The raised side of the button (if applicable), a careful " +
        "shade darker than background, has to balance with border to look " +
        "good.",
        order=15)
    side.save()
    text_color = StyleLabel(
        name="Text Color",
        group=group1,
        help_text="Color of text/icon on button, also tune font shadow if " +
        "changed.",
        order=20)
    text_color.save()
    text_shadow = StyleLabel(
        name="Text Shadow",
        group=group1,
        help_text="A shade just above the text/icon, should be the opposite " +
        "of the text color - light if it's dark and vice versa.",
        order=25)
    text_shadow.save()

    # primary button
    v1 = StyleProperty.objects.get(pk=28)
    v1.element = primary_button
    v1.label = background
    v1.save()
    val1 = StyleValue.objects.get(pk=28)
    val1.value = "rgba(0,179,0,1)"
    val1.parseable_values = val1.value
    val1.save()
    v2 = StyleProperty.objects.get(pk=29)
    v2.element = primary_button
    v2.label = border
    v2.save()
    val2 = StyleValue.objects.get(pk=29)
    val2.value = "rgba(0,95,0,1)"
    val2.parseable_values = val2.value
    val2.save()
    v3 = StyleProperty.objects.get(pk=30)
    v3.element = primary_button
    v3.label = text_color
    v3.save()
    val3 = StyleValue.objects.get(pk=30)
    val3.value = "rgba(255,255,255,1)"
    val3.parseable_values = val3.value
    val3.save()

    selector1 = StyleSelector(
        selector=".gbe-btn-primary, .btn.gbe-btn-primary",
        description="primary button & focus (to override bootstrap)",
        pseudo_class="focus",
        used_for="Forms",
        )
    selector1.save()
    prop1 = StyleProperty(selector=selector1,
                          label=text_shadow,
                          element=primary_button,
                          style_property="text-shadow",
                          value_type="px px px rgba",
                          value_template="{}px {}px {}px {}")
    prop1.save()
    val4 = StyleValue(value="0px -1px 0px rgba(0,0,0,0.5)",
                      parseable_values="0 -1 0 rgba(0,0,0,0.5)",
                      style_property=prop1,
                      style_version=val3.style_version)
    val4.save()

    # secondary button
    v4 = StyleProperty.objects.get(pk=61)
    v4.element = secondary_button
    v4.label = background
    v4.save()
    v5 = StyleProperty.objects.get(pk=62)
    v5.element = secondary_button
    v5.label = border
    v5.save()
    v6 = StyleProperty.objects.get(pk=63)
    v6.element = secondary_button
    v6.label = text_color
    v6.save()

    # light button
    v7 = StyleProperty.objects.get(pk=76)
    v7.element = light_button
    v7.label = background
    v7.save()
    v8 = StyleProperty.objects.get(pk=77)
    v8.element = light_button
    v8.label = border
    v8.save()
    v9 = StyleProperty.objects.get(pk=78)
    v9.element = light_button
    v9.label = text_color
    v9.save()

    # disabled button
    v10 = StyleProperty.objects.get(pk=82)
    v10.element = disabled_button
    v10.label = background
    v10.save()
    v11 = StyleProperty.objects.get(pk=83)
    v11.element = disabled_button
    v11.label = border
    v11.save()
    v12 = StyleProperty.objects.get(pk=84)
    v12.element = disabled_button
    v12.label = text_color
    v12.save()

    # ticket buy button
    v13 = StyleProperty.objects.get(pk=266)
    v13.element = buy_button
    v13.label = background
    v13.save()
    v14 = StyleProperty.objects.get(pk=265)
    v14.element = buy_button
    v14.label = text_color
    v14.save()

    # icon button
    v15 = StyleProperty.objects.get(pk=35)
    v15.hidden = True
    v15.save()
    v16 = StyleProperty.objects.get(pk=36)
    v16.hidden = True
    v16.save()
    v17 = StyleProperty.objects.get(pk=37)
    v17.hidden = True
    v17.save()


def destroy_style(apps, schema_editor):
    StyleElement = apps.get_model("gbe", "StyleElement")
    StyleLabel = apps.get_model("gbe", "StyleLabel")
    TestURL = apps.get_model("gbe", "TestURL")
    StyleGroup = apps.get_model("gbe", "StyleGroup")
    StyleElement.objects.all().delete()
    StyleLabel.objects.all().delete()
    TestURL.objects.all().delete()
    StyleGroup.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0014_auto_20210804_1715'),
    ]

    operations = [
        migrations.RunPython(initialize_style, reverse_code=destroy_style),
    ]
