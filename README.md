# CommentCounter
A Bot that counts reddit comments

Run tests with pytest:
```
python3 -m pytest
```
Or prevent output supression to debug tests
```
python3 -m pytest -s
```

Ensure you have created a `praw.ini` based of off `praw.template.ini`, and start the bot with `python3 App.py`.

Summon bot with `/u/{botname} {term_1} {term_2} ... {term_n}`.
Bot will reply with a table of counts for the number of top-level comments in the thread containing each term.