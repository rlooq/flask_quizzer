# FLASK QUIZZER

A very simple app for students or quiz geeks. It lets the user choose quizzes in different categories, answer them, and check the result, which is stored to be shown in each user's profile.  

It uses a `SQLite` database for user and score management. The questions in the quizzes are stored in a JSON file and managed with `TinyDB`, which may not be ideal for many concurrent users, but this was my first Flask project and it works for me and my small class. The code is probably not very efficient, and could be optimized in many ways, but I haven't had time to look at this for a while.

The tests in the `tests` folder are incomplete.
