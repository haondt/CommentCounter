# CommentCounter
A Bot that counts reddit comments

![image](https://user-images.githubusercontent.com/19233365/160250795-88ce6609-f888-4599-8658-a343e0b74e47.png)

Run tests with pytest:
```
python3 -m pytest
```
Or prevent output supression to debug tests
```
python3 -m pytest -s
```

Ensure you have created a `praw.ini` based of off `praw.template.ini`, and start the bot with `python3 App.py`.
The bot will exit gracefully when stopped with `Ctrl+c`. 

Summon bot with `/u/{botname} {term_1} {term_2} ... {term_n}`.
Bot will reply with a table of counts for the number of top-level comments in the thread containing each term.


