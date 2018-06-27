#!/usr/bin/env python
import bz2, os, zipfile, json, codecs
from fabric.api import run, sudo, task, get, put, env

global website, git, mysql_backup, mysql, setting_file


@task
def testlive():
    run("ls /var/backups/mysql/")

@task
def read_config_file(arg):
  with open('fabric.json') as infile:
    data = json.load(infile)
    env.website = arg
    env.git = data['website'][arg]['git']
    env.mysql_backup = data['website'][arg]['mysql_backup']
    env.mysql = data['website'][arg]['mysql']
    env.setting_file = data['website'][arg]['setting_file']
    print(git)
    download(env.mysql_backup)

@task
def download(arg):
    """ Usage: fab -H server1 download:"/path/to/file" """
    print(env.git)
    print('downloading the backup file')
    get(remote_path=arg, local_path=".", use_sudo=False)
    bz2file = os.path.basename(arg)
    print(bz2file)
    sql_name = os.path.splitext(bz2file)[0]
    print('unzipping file: {}').format(bz2file)
    os.system('bunzip2 ' + bz2file)
    create_mysqldb(sql_name)

def create_mysqldb(arg):
  database_name = os.path.splitext(arg)[0]

  print('creation of MYSQL DB')
  print('dropping the database')
  os.system('mysql -u root -e "drop database {};"'.format(database_name))
  print('creating the database')
  os.system('mysql -u root -e "create database {};"'.format(database_name))
  print('importing the database')
  os.system('mysql -u root {db_name} < {db_sql}'.format(db_name = database_name, db_sql = arg))
  git(database_name)

def git(arg):
  if os.path.exists(env.website):
    print (env.website + " Directory Exist! Folder will be deleted and git cloned")
    os.system('rm -rf ' + env.website)
  else:
    print(env.website + " Directory Does Not Exist! Folder will be cloned")
  os.system(env.git)

  '''
  elif arg == "laperigourdine":
    if os.path.exists("./perigourdine"):
      print "Perigourdine Directory Exist! Folder will be deleted and git cloned"
      os.system('rm -rf ./perigourdine')
    else:
      print "Perigourdine Directory Does Not Exist! Folder will be cloned"
    os.system('git clone git@git.mitija.com:websites/perigourdine.git')
  '''
  setting_file(arg);

def setting_file(arg):
  print('setting file will be copied');
  os.system('cp ' + env.setting_file)
  print('move git folder to the %s folder' % (env.website,))
  copy_folder = "sudo mkdir -p /var/www/{0}.local && sudo mv public_html /var/www/{0}.local".format(env.website)
  os.system("sudo rm -rf /var/www/{0}.local".format(env.website))
  os.system('mv {} public_html'.format(env.website))
  os.system(copy_folder)
  '''
  if arg == "la perigourdine":
    os.system('cp configuration_files/perigourdine/settings.php perigourdine/sites/default/')
    print('move git folder to the Perigourdine folder')
    os.system('sudo mkdir -p /var/www/perigourdine.local && sudo mv perigourdine/ /var/www/upa.local/public_html')
  else:
    print('the website is not implemented in the script!')
  '''

@task
def dc(arg):
    #download(arg)
    read_config_file(arg)
