import os, click, json, requests, datetime, shutil


def get_host_info(host_alias):
    return config['hosts'][host_alias]


def get_dashboards(host_alias,params=None):
    '''
    valid params:
    query str:partial match on title
    starred str:true/false
    '''
    host_entry=get_host_info(host_alias)
    response = requests.get(url='http://{}:{}/api/search'.format(host_entry['host'], host_entry['port']),
                            headers={'authorization':'Bearer {}'.format(host_entry['auth_token'])},
                            params=params
                            )
    return response.json()


def get_dashboards_in_backup(backupfolder):
    try:
        with open(os.path.join(backupfolder, config['app_config']['results_file'])) as bf:
            jbf = json.load(bf)
            return {'src': jbf['host'], 'dashboards': jbf['backup_results']}
    except IOError as e:
        print 'backup_results not found'
        pass


def get_backups(backup_path):
    backups = list()
    for directory in os.listdir(backup_path):
        backup_file = os.path.join(backup_path, directory, config['app_config']['results_file'])
        if os.path.isfile(os.path.join(backup_path, backup_file)):
            backup = {'name': directory, 'ctime': datetime.datetime.fromtimestamp(os.path.getctime(backup_file))}
            backups.append(backup)
    return backups


def build_uri_list(host_alias, dashboards):
    if dashboards == 'all':
        returnlist = list()
        for dash in get_dashboards(host_alias=host_alias):
            returnlist.append(dash['uri'])
    elif dashboards == 'none':
        returnlist = list()
    else:
        returnlist = dashboards.split(',')
    return returnlist


def backup_dash(host_alias, dashboard_uri, backup_path):
    host = get_host_info(host_alias)
    if dashboard_uri[0:3] == 'db/':
        dashboard_uri = dashboard_uri[3:]
    backup_file = os.path.join(backup_path, dashboard_uri)
    backup_record = dict()
    backup_record['uri'] = dashboard_uri
    with open(backup_file, 'wb') as fd:
        response = requests.get(url='http://{}:{}/api/dashboards/db/{}'.format(host['host'], host['port'], dashboard_uri),
                                headers={'authorization': 'Bearer {}'.format(host['auth_token'])}
                                )
        if response.status_code == 200:
            dash_source = response.json()
            backup_record['version'] = dash_source['meta']['version']
            backup_record['id'] = dash_source['dashboard']['id']
            fd.write(response.content)
        else:
            backup_record['version'] = None
            backup_record['id'] = None
            print 'Backup of dashboard {} failed [status code {}]'.format(dashboard_uri, response.status_code)

        backup_record['status_code'] = response.status_code
    return backup_record


def delete_dash(host_alias, dashboard_uri):
    host = get_host_info(host_alias)
    if dashboard_uri[0:3] == 'db/':
        dashboard_uri = dashboard_uri[3:]
    response = requests.delete(url='http://{}:{}/api/dashboards/db/{}'.format(host['host'], host['port'], dashboard_uri),
                            headers={'authorization': 'Bearer {}'.format(host['auth_token'])}
                            )
    if response.status_code == 200:
        print 'Deleted {}'.format(dashboard_uri)
    else:
        print 'Deletion of {} failed with return code {}'.format(dashboard_uri, response.status_code)


def restore_dash(host_alias,dashboard_uri,backup_directory,replace=False):
    if dashboard_uri[0:3] == 'db/':
        dashboard_uri = dashboard_uri[3:]
    print 'Restoring Dashboard {1} to host {0} from backup {2}.  Replace={3}'.format(
                                                        host_alias, dashboard_uri, backup_directory, replace)
    host = get_host_info(host_alias)
    existing_dashlist = get_dashboards(host_alias)
    restore_file = os.path.join(backup_directory, dashboard_uri)
    replacement_ok = False                    #initialize replacement variable to err to caution
    request_data = dict()

    try:
        with open(restore_file) as bf:                  #load dashboard data from backupfile
            request_data['dashboard'] = json.load(bf)['dashboard']
            request_data['dashboard']['id'] = None      #null out id, let grafana handle it
    except IOError as e:
        print 'unable to open file {}'.format(restore_file)
        return False

    if replace:               #Check if a dashboard of the current title already exists
        for dash in existing_dashlist:
            if dash['title'] == request_data['dashboard']['title']:
                replacement_ok = True

    if not replacement_ok:
        request_data['overwrite'] = False
    else:
        request_data['overwrite'] = True

    response = requests.post(url='http://{}:{}/api/dashboards/db'.format(
        host['host'], host['port'], dashboard_uri),
        data=json.dumps(request_data),
        headers={'authorization': 'Bearer {}'.format(host['auth_token']), 'Content-Type': 'application/json'}
        )
    if response.status_code != 200:
        print 'Sending data to URL: {} '.format(response.url)
        print 'Restore failed with status code {}'.format(response.status_code)
        print 'Response Content: {}'.format(response.content)
        return False
    else:
        return True


@click.group()
def manage():
    pass


@manage.command()
@click.option('--list', is_flag=True)
@click.argument('host')
def dashboard(**kwargs):
    if kwargs['list']:
        for dash in get_dashboards(host_alias=kwargs['host']):
            print 'ID: {}, Title: {}, URI: {}'.format(dash['id'], dash['title'], dash['uri'])


@manage.command()
@click.option('--dashboards', default='all', help='CSV list of dashboards to backup, defaults to all')
@click.option('--prune', is_flag=True, help='If supplied, will prune old dashboards (\'old\' is defined by json config file in CWD)')
@click.option('--list', is_flag=True)
@click.argument('host')
def backup(**kwargs):
    backup_root = config['app_config']['backup_location']
    if kwargs['list']:
        print 'listing known backups'
        for backup in get_backups(backup_root):
            backup_results = get_dashboards_in_backup(os.path.join(backup_root, backup['name']))
            if backup_results['src'] == kwargs['host']:
                if backup_results['src'] == kwargs['host']:
                    print 'Backup Location:{} (SRC:{})'.format(backup['name'],backup_results['src'])
                    for dash in backup_results['dashboards']:
                        print '  ID: {} URI: {} VERSION: {} STATUS: {}'.format(dash['id'], dash['uri'], dash['version'], dash['status_code'])

    else:
        backup_path = os.path.join(config['app_config']['backup_location'],
                                   datetime.datetime.now().strftime('%Y%m%dT%H:%M:%S'))
        if kwargs['dashboards']:
            results_file = dict()
            results_file['host'] = kwargs['host']
            results_file['backup_results'] = []
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            uri_list = build_uri_list(host_alias=kwargs['host'], dashboards=kwargs['dashboards'])
            for dash in uri_list:
                print 'backing up {}'.format(dash)
                results_file['backup_results'].append(backup_dash(host_alias=kwargs['host'], dashboard_uri=dash,
                                                                  backup_path=backup_path))
            with open(os.path.join(backup_path, config['app_config']['results_file']), 'wb') as fd:
                json.dump(results_file,fd)

        if kwargs['prune']:
            print 'Purging backups older than {} days'.format(config['app_config']['days_to_keep'])
            purge_to_date=datetime.datetime.now() - datetime.timedelta(days=float(config['app_config']['days_to_keep']))
            for backup in get_backups(kwargs['host'], backup_root):
                backup_path = os.path.join(backup_root, backup['name'])
                if backup['ctime'] <= purge_to_date:
                    print 'Deleting backup: {}'.format(backup_path)
                    shutil.rmtree(path=backup_path, ignore_errors=True)


@manage.command()
@click.option('--dashboards', default='none', help='CSV list of dashboards to delete, defaults to none')
@click.argument('host')
def delete(**kwargs):
    uri_list = build_uri_list(host_alias=kwargs['host'], dashboards=kwargs['dashboards'])
    if len(uri_list) > 0:
        print 'Deleting dashboards:'
    else:
        print 'No dashboards specified for deletion'
    for dash_uri in uri_list:
        delete_dash(kwargs['host'], dash_uri)


@manage.command()
@click.option('--dashboards', default='none', help='CSV list of dashboards to restore, defaults to *NONE* by default (the safe thing to do)')
@click.option('--frombackup', default='last', help='backup designator to restore from.  Use \'grafana_manage backup list\' for a listing')
@click.option('--replace', is_flag=True, help='Flag to determine if a dashboard should be overwritten')
@click.argument('host')
def restore(**kwargs):

    if kwargs['frombackup'] == 'last':
        backup_folders = os.listdir(config['app_config']['backup_location'])   #get folders in sorted order
        backup_folders.sort()
        backup_folder = backup_folders[-1]   #pull last item off the sorted path
        print 'Using last backup folder of {}'.format(backup_folder)
    else:
        backup_folder = kwargs['frombackup']

    restore_from_directory=os.path.join(os.path.join(config['app_config']['backup_location'], backup_folder))
    backup_dashlist = get_dashboards_in_backup(restore_from_directory)['dashboards']

    if kwargs['dashboards'] == 'none':
        restore_dashlist={}
    elif kwargs['dashboards'] == 'all':
        restore_dashlist = backup_dashlist
    else:
        restore_dashlist = kwargs['dashboards'].split(',')

    # print 'restoring dashboards {}'.format(restore_dashlist)

    for dash in restore_dashlist:
        print 'restoring dashboard: {}'.format(dash['uri'])
        restore_dash(host_alias=kwargs['host'], dashboard_uri=dash['uri'],
             backup_directory=restore_from_directory, replace=kwargs['replace'])


@manage.command()
@click.argument('source')
@click.argument('destination')
def sync(**kwargs):
    print 'Gathering dashboard info:'
    source_host     = get_host_info(kwargs['source'])
    dest_host       = get_host_info(kwargs['destination'])
    source_dashlist = get_dashboards(kwargs['source'])
    dest_dashlist   = get_dashboards(kwargs['destination'])
    request_data    = dict()

    for source_dash in source_dashlist:
        print 'Syncing {}'.format(source_dash['title'])
        replacement_ok = False  #set replacement_ok negative initially, only replace if we know we can
        get_response = requests.get(url='http://{}:{}/api/dashboards/{}'.format(source_host['host'], source_host['port'], source_dash['uri']),
                                headers={'authorization': 'Bearer {}'.format(source_host['auth_token'])}
                                )
        if get_response.status_code == 200:
            dash_source = get_response.json()
        else:
            print 'Failed to retrieve {} dashboard.  Status code {}'.format(source_dash['uri'], get_response.status_code)
        request_data['dashboard'] = dash_source['dashboard']
        request_data['dashboard']['id'] = None  # null out id, let grafana handle it

        for dest_dash in dest_dashlist:
            if dest_dash['title'] == source_dash['title']:
                replacement_ok = True

        if not replacement_ok:
            request_data['overwrite'] = False
        else:
            request_data['overwrite'] = True

        response = requests.post(url='http://{}:{}/api/dashboards/db'.format(
            dest_host['host'], dest_host['port']),
            data=json.dumps(request_data),
            headers={'authorization': 'Bearer {}'.format(dest_host['auth_token']), 'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print 'Sending data to URL: {} '.format(response.url)
            print 'Restore failed with status code {}'.format(response.status_code)
            print 'Response Content: {}'.format(response.content)


@manage.command()
def showconfig(**kwargs):
    print "Hosts:"
    for host_entry in config['hosts']:
        # print 'Host Alias: {}, {}'.format(host,type(host))
        for item in config['hosts'][host_entry]:
            print '  {}: {}'.format(item, config['hosts'][host_entry][item])
    print "app_config:"
    for item in config['app_config']:
        print '  {}: {}'.format(item, config['app_config'][item])

if __name__ == '__main__':
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'grafana_manager.json') # other option is os.getcwd()
    if os.path.isfile(config_file):
        with open(config_file) as data_file:
            config = json.load(data_file)
        manage()
    else:
        print 'grafana_manager.json not found in script working path'
