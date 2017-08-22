

MONTH_CHOICES = (
    ('January','January'),
    ('February', 'February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','Docember'),
)



WIDGET_SYNC = {
		'prod_utili': 'productivity_trends', 
		'external_accuracy': 'external_error_accuracy', 
		'internal_accuracy': 'internal_error_accuracy', 
		'productivity': 'productivity_chart', 
		'tat': 'TAT Graph', 
		'fte_utilisation': 'fte_utilization', 
		'operational_utilization': 'operational_utilization', 
		'absenteeism': 'absenteeism',
		'attrition': 'attrition'

}



DEFAULT_TARGET = {
        'prod_utili': 99, 
        'external_accuracy': 99, 
        'internal_accuracy': 99, 
        'productivity': 99, 
        'tat': 99, 
        'fte_utilisation': 80, 
        'operational_utilization': 99, 
        'absenteeism': 5,
        'attrition': 3
}

REVERSE_TARGET = ["absenteeism", "attrition"]