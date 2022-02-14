import re

def is_mention(username, comment):
    body = comment.body.lower()
    username_lower = username.lower()
    regex = fr"(^|^.*\s)/?u/{username_lower}($|\s.*$)"
    return re.match(regex, body) and hasattr(comment, 'submission')