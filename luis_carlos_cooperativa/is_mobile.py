from django_user_agents.utils import get_user_agent

def is_mobile(request):
    return get_user_agent(request).is_mobile


def get_profile_template(mobile_path, desktop_path, request):
    return mobile_path if is_mobile(request) else desktop_path
