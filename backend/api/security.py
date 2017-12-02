
from api.review_views import get_all_related_user


def get_permitted_user(project, center, user):
	"""Check whether the user is permitted for the project or not
	"""
	var = 'Valid User'
    if project and center:
		user_dict = get_all_related_user(project, center)
		if user not in user_dict['id_list']:
			var = 'Invalid User'

	return var
