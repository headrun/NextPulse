

from api.review_views import get_all_related_user


def get_permitted_user(project, center, user):
	"""Check whether the user is permitted for the project or not
	"""

	user_dict = get_all_related_user(project, center)
	if user.id in user_dict['id_list']:
		return 'Valid User'
	else:
		return 'Invalid User'

