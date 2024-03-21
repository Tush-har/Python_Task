## edgeserver

This repository is for managing code for ACYM\
\
\
Initialise git in local folder using the following command

1. 

\#git init

2. Configure username and email address

\#git config --global user.name <username>

\#git config --global user.email <email>

3. Once you have a remote repository, add it as a remote to your local repository using the git remote add command. Replace <remote-name> with a name for your remote (e.g., "notes"), and <remote-url> with the URL of your remote repository

\#git remote add <remote-name> <remote-url>

\#git remote add origin http://192.168.10.39:8445/repo.git

4. Pull code from gitblit first

\#git pull https://github.com/abc/xyz.git

5. Verify

\#git config --list

6. Add/Create files (code)

7. Add files to staging area

\#git add . // . specifies current directory

8. Commit the code to local repository

\#git commit -m initial_commit // -m is commit message

9. Push the code to central repository

\#git push -u origin master //main specifies the branch