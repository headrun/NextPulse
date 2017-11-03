



HANGUP_OPTIONS = (
		('Caller Disconnect', 'Caller Disconnect'),
		('Agent Disconnect', 'Agent Disconnect'),
	)

STATUS_OPTIONS = (
		('Answered', 'Answered'),
		('Unanswered', 'Unanswered'),
	)

CALL_TYPE_OPTIONS = (
		('Manual', 'Manual'),
		('Automatic', 'Automatic'),
	)


SECONDS_STORAGE = ['time to answer', 'talk time', 'hold time', 'duration', 'wrapup duration', 'handling time',\
					'total talk time', 'total wrapup time', 'total pause time', 'total idle time',\
					'total login duration']

DATETIME_STORAGE = ['start time', 'end time']

DATES = ['date', 'call date']

INTEGER_NUMBERS = ['total calls', 'connected calls', 'abandoned calls']

CANCEL_DISPOSITION = []

CONVERT_TO_DAILY = ['Inbound Hourly', 'Outbound Hourly']

TRANSFER = {'agent_transfer_list': 'AgentTransferCall', 'skill_transfer_list': 'SkillTransferCall',\
				'location_transfer_list': 'LocationTransferCall', 'disposition_transfer_list': 'DispositionTransferCall'}