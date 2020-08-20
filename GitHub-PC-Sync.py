# https://pygithub.readthedocs.io/en/latest/introduction.html
import sys
import os
import subprocess
import datetime

if sys.version_info < (3,):
    print('Must use Python version 3')
    sys.exit()

from github import Github


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def rm_file(f):
    if os.path.exists(f):
        os.remove(f)

def log_entry(org, repo, push, pull, new, **kwargs):
    if not kwargs:
        timestamp = datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S %p')
        path, dirs, files = next(os.walk(os.path.join(_cwd, org, repo.name)))
        with open(log, 'a') as f:
            f.write('\n{},{},{},{},{},{},{},{}'.format(timestamp, org, repo.name, push, pull, new, len(files), repo.html_url))
    else:
        timestamp = datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S %p')
        path, dirs, files = next(os.walk(os.path.join(_cwd, org, repo)))
        with open(log, 'a') as f:
            f.write('\n{},{},{},{},{},{},{},{}'.format(timestamp, org, repo, push, pull, new, len(files), kwargs['url']))

# ==============================================================================
# GLOBAL VARIABLES
# ==============================================================================
_cwd = os.path.dirname(os.getcwd())
master_dir = os.path.join(_cwd, 'geocoug-master')
archive_dir = os.path.join(_cwd, 'geocoug-archive')
working_dir = os.path.join(_cwd, 'geocoug-working')
wsc_dir = os.path.join(_cwd, 'geocoug-wsc')
mhk_dir = os.path.join(_cwd, 'mhk-env')
misc_dir = os.path.join(_cwd, 'miscellaneous')

temp_bat = os.path.join(_cwd, 'temp.bat')

log = os.path.join(os.getcwd(), 'sync_log.txt')

# create a Github instance using an access token
g = Github("github-key")
github_user = g.get_user().login

organizations = ['geocoug-master',
                 'geocoug-archive',
                 'geocoug-working',
                 'geocoug-wsc',
                 'mhk-env',
                 'miscellaneous'
                ]

excluded_repos = []

def fetchRepos():
    print('\nFetching PC and GitHub repos:')

    pc_master_repos = [repo for repo in os.listdir(master_dir) if repo not in excluded_repos]
    github_master_repos = [repo.name for repo in g.get_user().get_repos() if repo.name not in excluded_repos and repo.organization is None]
    print('   User         : {}'.format(github_user))
    print('   PC repos     : {}'.format(len(pc_master_repos)))
    print('   GitHub repos : {}\n'.format(len(github_master_repos)))

    pc_archive_repos = [repo for repo in os.listdir(archive_dir) if repo not in excluded_repos]
    github_archive_repos = [repo.name for repo in g.get_organization('geocoug-archive').get_repos() if repo.name not in excluded_repos]
    print('   Organization : {}'.format(os.path.basename(archive_dir)))
    print('   PC repos     : {}'.format(len(pc_archive_repos)))
    print('   GitHub repos : {}\n'.format(len(github_archive_repos)))

    pc_working_repos = [repo for repo in os.listdir(working_dir) if repo not in excluded_repos]
    github_working_repos = [repo.name for repo in g.get_organization('geocoug-working').get_repos() if repo.name not in excluded_repos]
    print('   Organization : {}'.format(os.path.basename(working_dir)))
    print('   PC repos     : {}'.format(len(pc_working_repos)))
    print('   GitHub repos : {}\n'.format(len(github_working_repos)))

    pc_wsc_repos = [repo for repo in os.listdir(wsc_dir) if repo not in excluded_repos]
    github_wsc_repos = [repo.name for repo in g.get_organization('Western-States-Consult').get_repos() if repo.name not in excluded_repos]
    print('   Organization : {}'.format(os.path.basename(wsc_dir)))
    print('   PC repos     : {}'.format(len(pc_wsc_repos)))
    print('   GitHub repos : {}\n'.format(len(github_wsc_repos)))

    pc_mhk_repos = [repo for repo in os.listdir(mhk_dir) if repo not in excluded_repos]
    github_mhk_repos = [repo.name for repo in g.get_organization('mhk-env').get_repos() if repo.name not in excluded_repos]
    print('   Organization : {}'.format(os.path.basename(mhk_dir)))
    print('   PC repos     : {}'.format(len(pc_mhk_repos)))
    print('   GitHub repos : {}\n'.format(len(github_mhk_repos)))

    pc_misc_repos = [repo for repo in os.listdir(misc_dir) if repo not in excluded_repos]
    print('   Organization : {}'.format(os.path.basename(misc_dir)))
    print('   PC repos     : {}\n'.format(len(pc_misc_repos)))

    print('-' * 75)

    repo_dict = {
        'geocoug-master': {'pc_master_repos': pc_master_repos,
                           'github_master_repos': github_master_repos},
        'geocoug-archive': {'pc_archive_repos': pc_archive_repos,
                            'github_archive_repos': github_archive_repos},
        'geocoug-working': {'pc_working_repos': pc_working_repos,
                            'github_working_repos': github_working_repos},
        'geocoug-wsc': {'pc_wsc_repos': pc_wsc_repos,
                        'github_wsc_repos': github_wsc_repos},
        'mhk-env': {'pc_mhk_repos': pc_mhk_repos,
                    'github_mhk_repos': github_mhk_repos},
        'miscellaneous': {'pc_misc_repos': pc_misc_repos}
    }

    return repo_dict


# ==============================================================================
# GitHub_to_PC()
#   Pulls GitHub repos to PC and creates a new directory if it doesnt exist
# ==============================================================================
def GitHub_to_PC(repo_dict):

    def gitPull(repo, org, initRemote):
        if org != 'miscellaneous':
            rm_file(temp_bat)
            with open(temp_bat, 'w') as f:
                f.write("cd {}\{}\{} \n".format(_cwd, org, repo.name))
                if initRemote:
                    f.write("git init \n")
                    f.write("git remote add origin {} \n".format(repo.html_url))
                else:
                    pass
                f.write("git pull origin master")
            os.system(temp_bat)
            rm_file(temp_bat)
        else:
            rm_file(temp_bat)
            with open(temp_bat, 'w') as f:
                f.write("cd {}\{}\{} \n".format(_cwd, org, repo))
                f.write("git pull origin master")
            os.system(temp_bat)
            rm_file(temp_bat)

    def pullRepos(org, pc_repos, github_repos):
        if org == 'geocoug-master':
            for repo_name in github_repos:
                if repo_name in excluded_repos:
                    pass
                else:
                    repo = g.get_user().get_repo(repo_name)
                    print('PULLING REPOSITORY')
                    print('   User   : ', github_user)
                    print('   Repo   : ', repo.name)

                    if os.path.exists(os.path.join(master_dir, repo.name)):
                        if os.path.exists(os.path.join(master_dir, repo.name, '.git/config')):
                            config = os.path.join(master_dir, repo.name, '.git/config')
                            with open(config, 'r') as f:
                                lines = f.readlines()
                            lines = [x.strip() for x in lines]
                            for line in range(len(lines)):
                                if lines[line] == '[remote "origin"]':
                                    if "url =" in lines[line + 1]:
                                        remote_url = lines[line+1].split("=")[1].strip()
                                        print('   Remote : ', remote_url)
                                        gitPull(repo, org, False)
                                        log_entry(org, repo, False, True, False)
                                    else:
                                        gitPull(repo, org, True)
                                        log_entry(org, repo, False, True, True)
                    else:
                        os.mkdir(os.path.join(master_dir, repo.name))
                        gitPull(repo, org, True)
                        log_entry(org, repo, False, True, True)
                    print('-' * 75)
                    print('\n')

        elif org == 'miscellaneous':
            for repo_name in pc_repos:
                if repo_name in excluded_repos:
                    pass
                else:
                    if os.path.exists(os.path.join(misc_dir, repo_name)):
                        print('PULLING REPOSITORY')
                        print('   Org    : ', org)
                        print('   Repo   : ', repo_name)
                        if os.path.exists(os.path.join(misc_dir, repo_name, '.git/config')):
                            config = os.path.join(misc_dir, repo_name, '.git/config')
                            with open(config, 'r') as f:
                                lines = f.readlines()
                            lines = [x.strip() for x in lines]
                            for line in range(len(lines)):
                                if lines[line] == '[remote "origin"]':
                                    if "url =" in lines[line + 1]:
                                        remote_url = lines[line+1].split("=")[1].strip()
                                        print('   Remote : ', remote_url)
                                        gitPull(repo_name, org, False)
                                        log_entry(org, repo_name, False, True, False, url=remote_url)
                    else:
                        pass
                    print('-' * 75)
                    print('\n')

        else:
            for repo_name in github_repos:
                if repo_name in excluded_repos:
                    pass
                else:
                    if org == 'geocoug-wsc':
                        repo = g.get_organization('Western-States-Consult').get_repo(repo_name)
                    else:
                        repo = g.get_organization(org).get_repo(repo_name)

                    print('PULLING REPOSITORY')
                    print('   Org    : ', org)
                    print('   Repo   : ', repo.name)

                    if os.path.exists(os.path.join(_cwd, org, repo.name)):
                        if os.path.exists(os.path.join(_cwd, org, repo.name, '.git/config')):
                            config = os.path.join(_cwd, org, repo.name, '.git/config')
                            with open(config, 'r') as f:
                                lines = f.readlines()
                            lines = [x.strip() for x in lines]
                            for line in range(len(lines)):
                                if lines[line] == '[remote "origin"]':
                                    if "url =" in lines[line + 1]:
                                        remote_url = lines[line+1].split("=")[1].strip()
                                        print('   Remote : ', remote_url)
                                        gitPull(repo, org, False)
                                        log_entry(org, repo, False, True, False)
                                    else:
                                        gitPull(repo, org, True)
                                        log_entry(org, repo, False, True, True)
                    else:
                        os.mkdir(os.path.join(_cwd, org, repo.name))
                        gitPull(repo, org, True)
                        log_entry(org, repo, False, True, True)
                    print('-' * 75)
                    print('\n')

    # Start of GitHub_to_PC() content
    for org in organizations:
        if org == 'geocoug-master':
            pullRepos(org, repo_dict[org]['pc_master_repos'], repo_dict[org]['github_master_repos'])
        elif org == 'geocoug-archive':
            pullRepos(org, repo_dict[org]['pc_archive_repos'], repo_dict[org]['github_archive_repos'])
        elif org == 'geocoug-working':
            pullRepos(org, repo_dict[org]['pc_working_repos'], repo_dict[org]['github_working_repos'])
        elif org == 'geocoug-wsc':
            pullRepos(org, repo_dict[org]['pc_wsc_repos'], repo_dict[org]['github_wsc_repos'])
        elif org == 'mhk-env':
            pullRepos(org, repo_dict[org]['pc_mhk_repos'], repo_dict[org]['github_mhk_repos'])
        elif org == 'miscellaneous':
            pullRepos(org, repo_dict[org]['pc_misc_repos'], None)
        else:
            raise NameError("Organization <{}> not found for user <{}>".format(org, github_user))


# ==============================================================================
# PC_to_GitHub()
#   Pushes PC repos to GitHub.
#   If the repo doesnt exist on GitHub, a new repo will be created
#   Otherwise, the repo will be updated
# ==============================================================================
def PC_to_GitHub(repo_dict):

    def gitInit(repo, repo_url, org):
        if org == 'geocoug-master':
            _dir = master_dir
        elif org == 'geocoug-archive':
            _dir = archive_dir
        elif org == 'geocoug-working':
            _dir = working_dir
        elif org == 'geocoug-wsc':
            _dir = wsc_dir
        else:
            raise NameError("Organization <{}> not found for user <{}>".format(org, github_user))

        rm_file(temp_bat)
        with open(temp_bat, 'w') as f:
            f.write("cd {}\{} \n".format(_dir, repo.name))
            f.write("git init \n")
            f.write("git remote add origin {} \n".format(repo_url))
            f.write("git add --all \n")
            f.write('git commit -m "init" \n')
            f.write("git push -u origin master")
        os.system(temp_bat)
        rm_file(temp_bat)


    def initRepos(org, pc_repos, github_repos):
        if org == 'geocoug-master':
            _private = False
            isOrg = False
        else:
            _private = True
            isOrg = True

        repo_count = 0
        for repo_name in pc_repos:
            if repo_name in github_repos:
                repo_count += 1
                pass
            else:
                print('-' * 75)
                print('CREATING NEW GITHUB REPO')
                if isOrg:
                    print('   Org  : ', org)
                else:
                    print('   User : ', github_user)
                print('   Repo : ', repo_name)

                if not isOrg:
                    new_repo = g.get_user().create_repo("{}".format(repo_name), private=_private)
                    new_github_repo = g.get_user().get_repo(repo_name)
                    new_github_repo_url = new_github_repo.html_url
                else:
                    if org == 'geocoug-wsc':
                        new_repo = g.get_organization('Western-States-Consult').create_repo("{}".format(repo_name), private=_private)
                        new_github_repo = g.get_organization('Western-States-Consult').get_repo(repo_name)
                        new_github_repo_url = new_github_repo.html_url
                    else:
                        new_repo = g.get_organization(org).create_repo("{}".format(repo_name), private=_private)
                        new_github_repo = g.get_organization(org).get_repo(repo_name)
                        new_github_repo_url = new_github_repo.html_url

                gitInit(new_github_repo, new_github_repo_url, org)
                log_entry(org, repo_name, True, False, True, url=new_github_repo_url)


    # Start of PC_to_GitHub() content
    for org in organizations:
        if org == 'geocoug-master':
            initRepos(org, repo_dict[org]['pc_master_repos'], repo_dict[org]['github_master_repos'])
        elif org == 'geocoug-archive':
            initRepos(org, repo_dict[org]['pc_archive_repos'], repo_dict[org]['github_archive_repos'])
        elif org == 'geocoug-working':
            initRepos(org, repo_dict[org]['pc_working_repos'], repo_dict[org]['github_working_repos'])
        elif org == 'geocoug-wsc':
            initRepos(org, repo_dict[org]['pc_wsc_repos'], repo_dict[org]['github_wsc_repos'])
        elif org == 'mhk-env':
            pass
        elif org == 'miscellaneous':
            pass
        else:
            raise NameError("Organization <{}> not found for user <{}>".format(org, github_user))


if __name__ == "__main__":
    repo_dict = fetchRepos()
    print('\n\nPULLING GITHUB REPOS TO PC')
    print('='*75)
    GitHub_to_PC(repo_dict)
    print('\n\nPUSHING PC REPOS TO GITHUB')
    print('='*75)
    PC_to_GitHub(repo_dict)
    print('\n\n\nDONE')
