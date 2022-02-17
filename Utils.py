import re
import time
from praw.models.util import BoundedSet, ExponentialCounter

def is_mention(username, comment):
    body = comment.body.lower()
    username_lower = username.lower()
    regex = fr"(^|^.*\s)/?u/{username_lower}($|\s.*$)"
    return re.match(regex, body) and hasattr(comment, 'submission')

def stream_generator(
    function,
    run_event=None,
    pause_after = None,
    skip_existing = False,
    attribute_name = "fullname",
    exclude_before = False,
    **function_kwargs):
    before_attribute = None
    exponential_counter = ExponentialCounter(max_counter=16)
    seen_attributes = BoundedSet(301)
    without_before_counter = 0
    responses_without_new = 0
    valid_pause_after = pause_after is not None
    while not run_event.is_set():
        found = False
        newest_attribute = None
        limit = 100
        if before_attribute is None:
            limit -= without_before_counter
            without_before_counter = (without_before_counter + 1) % 30
        if not exclude_before:
            function_kwargs["params"] = {"before": before_attribute}
        for item in reversed(list(function(limit=limit, **function_kwargs))):
            attribute = getattr(item, attribute_name)
            if attribute in seen_attributes:
                continue
            found = True
            seen_attributes.add(attribute)
            newest_attribute = attribute
            if not skip_existing:
                yield item
        before_attribute = newest_attribute
        skip_existing = False
        if valid_pause_after and pause_after < 0:
            yield None
        elif found:
            exponential_counter.reset()
            responses_without_new = 0
        else:
            responses_without_new += 1
            if valid_pause_after and responses_without_new > pause_after:
                exponential_counter.reset()
                responses_without_new = 0
                yield None
            else:
                if run_event is None:
                    time.sleep(exponential_counter.counter())
                else:
                    run_event.wait(exponential_counter.counter())
