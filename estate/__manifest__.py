{
    'name': 'Estate',
    'author': 'Bowmika',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/properties_views.xml',
        'views/properties_types_views.xml',
        'views/properties_tags_views.xml',
        'views/estateproperties.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False
}