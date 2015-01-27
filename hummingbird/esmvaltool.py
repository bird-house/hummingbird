from malleefowl import config
from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

def search(url, distrib, replica, limit, constraints, start_year, end_year, monitor):
    from malleefowl.esgf.search import ESGSearch
    esgsearch = ESGSearch(
        url = url,
        distrib = distrib,
        replica = replica,
        latest = True,
        monitor = monitor,
    )
    logger.info("constraints: %s", constraints)

    (result, summary, facet_counts) = esgsearch.search(
        constraints = constraints,
        query = "*:*",
        start = "%d-01-01" % start_year,
        end = "%d-12-31" % end_year,
        search_type = "File",
        limit = limit,
        offset = 0,
        temporal = False)
    return result

def download(urls, credentials, monitor):
    from malleefowl.download import download_files
    file_urls = download_files(
        urls = urls,
        credentials = credentials,
        monitor = monitor)
    return file_urls

def prepare(file_urls):
    # symlink files to workspace dir
    from urlparse import urlparse
    from os import mkdir,chmod, symlink
    from os.path import exists, basename, join, realpath, curdir, abspath
    workspace = abspath(join(curdir, 'workspace'))
    mkdir(workspace)
    # TODO: docker needs full access to create new files
    import stat
    chmod(workspace, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
    input_dir = join(workspace, 'input-data')
    mkdir(input_dir)
    results = []
    for url in file_urls:
        filename = realpath(urlparse(url).path)
        logger.debug('filename = %s', filename)
        if exists(filename):
            new_name = join(input_dir, basename(filename))
            # TODO: make sure symlinks work in docker container
            logger.debug("new name: %s", new_name)
            symlink(filename, new_name)
            results.append(new_name)
    return workspace

def generate_namelist(name, prefix, workspace,
                      model, experiment, cmor_table, ensemble, start_year, end_year,
                      docker=False):
    logger.info("generate namelist %s", name)

    if docker is True:
        prefix = "/home/esmval/esmvaltool"
        workspace = "/workspace"
    
    from os.path import join, dirname
    from mako.template import Template
    mytemplate = Template(
        filename=join(dirname(__file__), 'templates', 'namelist_%s.xml' % name),
        output_encoding='utf-8',
        encoding_errors='replace')
    return mytemplate.render_unicode(
        prefix=prefix,
        workspace=workspace,
        model=model,
        experiment=experiment,
        cmor_table=cmor_table,
        ensemble=ensemble,
        start_year=start_year,
        end_year=end_year,
        )
   
def write_namelist(namelist, workspace):
    from os.path import join, abspath
    #from tempfile import mkstemp
    #_,outfile = mkstemp(prefix='namelist_', suffix='.xml', dir=curdir)
    outfile = abspath(join(workspace, "namelist.xml"))
    with open(outfile, 'w') as fp:
        fp.write(namelist)
    return outfile

def run(namelist, prefix, workspace, docker=False):
    logfile = None
    if docker is True:
        logfile = run_docker(workspace=workspace)
    else:
        logfile = run_console(namelist=namelist, prefix=prefix)
    return logfile

def run_console(namelist, prefix):
    logger.info("run esmval on console: prefix=%s", prefix)
    logger.debug("namelist=%s", namelist)
    from os.path import join, curdir, abspath
    script = join(prefix, "esmval.sh")
    logfile = abspath(join(curdir, 'log.txt'))
    cmd = [script, namelist, logfile]

    from subprocess import check_output
    try:
        check_output(cmd)
    except:
        logger.exception('esmvaltool failed!')
    return logfile

def run_docker(workspace):
    logger.info("run esmval with docker")
    from os.path import abspath, curdir, join, realpath
    mountpoint = "%s:/workspace" % realpath(workspace)
    cmd = ["docker", "run", "--rm", "-t"]
    cmd.extend([ "-v", mountpoint])
    # archive path
    for archive in config.archive_root():
        if len(archive.strip()) < 3:
            logger.warn('suspicious archive root: %s', archive)
            continue
        logger.debug("mount archive root: %s", archive)
        cmd.extend(["-v", "%s:%s:ro" % (archive, archive)])
    # cache path
    cache_path = realpath(config.cache_path())
    cmd.extend(["-v", "%s:%s:ro" % (cache_path, cache_path)])
    cmd.extend(["birdhouse/esmvaltool"])

    from subprocess import check_call
    try:
        check_call(cmd)
    except:
        logger.exception('docker failed')
       
    return join(workspace, 'log.txt')

def run_on_esgf(
        project, model, variable, cmor_table, experiment, ensemble, start_year, end_year,
        distrib=False, replica=False, limit=10,
        credentials=None,
        monitor=None):
    # TODO: configure archive_root only in malleefowl
    from os import environ
    if not environ.has_key('ESGF_ARCHIVE_ROOT'):
        environ['ESGF_ARCHIVE_ROOT'] = config.getConfigValue("hummingbird", "archive_root")
    # get prefix of esmvaltool
    docker = False
    prefix = config.getConfigValue("hummingbird", "esmval_root")
    if prefix is None or len(prefix.strip()) == 0:
        docker = True

    # search
    constraints = []
    constraints.append( ("project", project ) )
    constraints.append( ("model", model ) )
    constraints.append( ("variable", variable ) )
    constraints.append( ("cmor_table", cmor_table ) )
    constraints.append( ("experiment", experiment ) )
    constraints.append( ("ensemble", ensemble ) )

    urls = search(
        url = config.getConfigValue("hummingbird", "esgsearch_url"),
        distrib=distrib,
        replica=replica,
        limit=limit,
        constraints=constraints,
        start_year=start_year,
        end_year=end_year,
        monitor=monitor
        )

    # download
    file_urls = download(
        urls=urls,
        credentials=credentials,
        monitor=monitor)

    # prepare workspace dir
    workspace = prepare(file_urls)

    # generate namelist
    namelist = generate_namelist(
        name="MyDiag",
        prefix=prefix,
        workspace=workspace,
        model=model,
        cmor_table=cmor_table,
        experiment=experiment,
        ensemble=ensemble,
        start_year=start_year,
        end_year=end_year,
        docker=docker,
        )
    f_namelist = write_namelist(namelist=namelist, workspace=workspace)

    # run esmvaltool
    monitor("esmvaltool started", 20)
    log_file = run(
        namelist=f_namelist, prefix=prefix, workspace=workspace, docker=docker)
    monitor("esmvaltool done", 100)

    # output: postscript
    # TODO: permisson problem with generated files within docker container
    import shutil
    out = 'output.ps'
    from os.path import join
    shutil.copyfile(join(workspace, 'plots', 'MyDiag', 'MyDiag_MyVar.ps'), out)

    return out, f_namelist, log_file
