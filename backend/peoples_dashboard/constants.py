

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


TARGETS = ['Charge Curator_single_target', 'Charge Curator_no_of_agents', 'Das_no_of_days', 'Das_single_target', 'Das_target',
            'Das_no_of_agents', 'Das_actual', 'Das_name', 'Charge Inspector_actual', 'Charge Inspector_no_of_days',
            'Charge Inspector_single_target', 'Charge Inspector_target', 'Charge Inspector_no_of_agents', 'Charge Inspector_name',
            'Partial QA_name', 'Partial QA_no_of_days', 'Partial QA_no_of_agents', 'Partial QA_single_target',
            'Partial QA_target', 'Partial QA_actual']

















