#GitHub-PC-Sync.py

Sync a local directory with GitHub.

My repositories are set up in multiple folders on my PC like so:

- \GitHub-Repos
  - \geocoug-master
  - \geocoug-archive
  - \geocoug-working
  - \geocoug-wsc
  - \mhk-env
  - \miscellaneous

"geocoug-master" contains my user repos, others represent organizations, miscellaneous represents pull only repos I use and want updated.

This script pulls all repositories for each remote, then pushes new directories that do not exist on GitHub for a specific org or user.

