# dynocms
This is a dynamic and highly configurable content management system to be used mainly by technically savvy users.

The main way to edit content is through the django admin section. Users add pages and for each page specify mainly its layout and various other parameters. 

The user can also add for each page a number of html widgets. Each widget has an order that fits with a layout section which is ordered as well.

In addition to generic HTML widgets (which the user can directly code) there area also a number of built in widgets such as a "Contact_us" widget and a "Wysiwyg" widget. Additional widgets must be coded into the system. Any existing widget can be used as an example template for that matter.

Pages also have viewing permissions which can be edited with the page edit form. Individual users or entire groups can be granted view permissions to any page.

DynoCMS also allows the user to enter a number of global site parameters such as site logo, HTML theme and css tamplates. There comes bundeled an example site complete with logo image and themes that are installed upon issuing a "syncdb" command.

The user can also edit the header, footer and page layouts. A handy macro facility is also provided with the system. Last but not least users can upload images to be used within html widgets.

##Installation
Clone repository then issue a `python manage.py syncdb` command.

##Dependencies
None