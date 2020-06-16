# SlackCalendar

A small bodgy project that creates a bot that automatically posts to slack what day to celebrate.

There is a lot of things that could (and should) be improved. Maybe I will do that in the future, maybe I wont.

Usage: add your slack api-token in the designated spot in the creds_xmpl.txt

scroll to the bottom of slack_calendar.py.
Initiate the slack calendar and call the run() method.

Initiation can be done with a few parameters:

* creds_file: (default "creds.txt"): the filename with your credentials
* datefile:(default ".date.txt"): the file where the date will be stored. This is used to check whether the bot has already posted sth today
* post_time: (default '8:00'): At what time the bot should post something everyday. Format "hh:mm"
* frequency: (default 15): how often the program checks if it needs to post sth.
* channel: (default '#oh_happy_day'): to what slack channel it should post.
