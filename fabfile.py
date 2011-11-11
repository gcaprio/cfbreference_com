import os

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

RSYNC_EXCLUDE = (
    '.DS_Store',
    '.hg',
    '.svn',	
    '*.pyc',
    '*.example',
    'media/admin',
    'media/attachments',
    'fabfile.py',
    'bootstrap.py',
)

# Remote Home Directory 
env.home = '/home/deploy'
# Target DNS name
env.domain = 'cfbreference.com'
# Remote Project Directory. Default: cfbreference.com
env.project = 'cfbreference_com'
# Remote User
env.user = 'deploy'
# Apache Root
env.apache_conf_root = "/etc/apache2/sites-available"

def _setup_path():
    # Destination site for this push.
    env.site = env.environment + "." + env.domain
    # Root directory for project.  Default: {env.home}/www/{env.site}
    env.root = os.path.join(os.path.join(env.home, "www"), env.site)
    # Root directory for source code.  Default: {env.root}/{env.project}
    env.code_root = os.path.join(env.root, env.project)
    # Remote virtualenv directory. Default: {env.home}/.virtualenvs/{env.site}
    env.virtualenv_root = os.path.join(os.path.join(env.home, '.virtualenvs'), env.site)
    # Target project settings file. Default: {env.project}.settings
    env.settings = '%s.settings' % env.project

def pro():
    # Target Environment sub-domain ( i.e. beta.domain.com, www.domain.com)
    env.environment = 'www'
    # Host Tuple List for deployment.
    env.hosts = ['173.203.212.245:13869']
    _setup_path()

def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    # Require a valid env.root value
    require('root', provided_by=('pro'))
    # Create env.root directory
    run('mkdir -p %(root)s' % env)
    
    create_virtualenv()
    deploy()
    update_requirements()


def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('pro'))
    args = '-v --clear'
    run('mkdir -p %s' % env.virtualenv_root)
    run('virtualenv %s %s' % (args, env.virtualenv_root))


def deploy():
    """ rsync code to remote host """
    require('root', provided_by=('pro'))
    if env.environment == 'pro':
        if not console.confirm('Are you sure you want to deploy production?', default=False):
            utils.abort('Production deployment aborted.')
    # defaults rsync options:
    # -pthrvz
    # -p preserve permissions
    # -t preserve times
    # -h output numbers in a human-readable format
    # -r recurse into directories
    # -v increase verbosity
    # -z compress file data during the transfer
    extra_opts = '--omit-dir-times'
    rsync_project(
        remote_dir=env.root,
        exclude=RSYNC_EXCLUDE,
        delete=True,
        extra_opts=extra_opts,
    )
    touch()
    update_apache_conf()

def update_requirements():
    """ update external dependencies on remote host """
    require('code_root', provided_by=('pro'))
    requirements = os.path.join(env.code_root, 'requirements')
    with cd(requirements):
        cmd = ['pip install']
        cmd += ['-E %(virtualenv_root)s' % env]
        cmd += ['--requirement %s' % os.path.join(requirements, 'apps.txt')]
        run(' '.join(cmd))


def touch():
    """ touch wsgi file to trigger reload """
    require('code_root', provided_by=('pro'))
    apache_dir = os.path.join(env.code_root, 'apache')
    with cd(apache_dir):
        run('touch %s.wsgi' % env.environment)


def update_apache_conf():
    """ upload apache configuration to remote host """
    require('root', provided_by=('pro'))
    source = os.path.join(os.path.join(env.code_root, 'apache'), '%(environment)s.conf' % env)
    dest = os.path.join(env.apache_conf_root, '%(environment)s.%(domain)s' % env)
    sudo('cp %s %s' % ( source, dest ))
    apache_reload()


def configtest():    
    """ test Apache configuration """
    require('root', provided_by=('pro'))
    run('apache2ctl configtest')


def apache_reload():    
    """ reload Apache on remote host """
    require('root', provided_by=('pro'))
    sudo('/etc/init.d/apache2 reload')


def apache_restart():    
    """ restart Apache on remote host """
    require('root', provided_by=('pro'))
    run('sudo /etc/init.d/apache2 restart')


def symlink_django():    
    """ create symbolic link so Apache can serve django admin media """
    require('root', provided_by=('pro'))
    admin_media = os.path.join(env.virtualenv_root,
                               'src/django/django/contrib/admin/media/')
    media = os.path.join(env.code_root, 'media/admin')
    if not files.exists(media):
        run('ln -s %s %s' % (admin_media, media))


def reset_local_media():
    """ Reset local media from remote host """
    require('root', provided_by=('pro'))
    media = os.path.join(env.code_root, 'media', 'upload')
    local('rsync -rvaz %s@%s:%s media/' % (env.user, env.hosts[0], media))
