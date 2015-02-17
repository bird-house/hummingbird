from malleefowl import config

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

def esmvaltool(namelist):
    prefix = config.getConfigValue("hummingbird", "esmval_root")
    logger.info("run esmvaltool: prefix=%s", prefix)
    logger.debug("namelist=%s", namelist)

    # set ncl path
    ncarg_root = config.getConfigValue("hummingbird", "ncarg_root")
    from os import environ
    environ['NCARG_ROOT'] = ncarg_root.strip()
    environ['PATH'] = environ['NCARG_ROOT'] + '/bin' + ':' + environ['PATH']
    logger.debug('path with ncarg_root: %s', environ['PATH'])
    
    from os.path import join, curdir, abspath
    script = join(prefix, "esmval.sh")
    logfile = abspath(join(curdir, 'log.txt'))
    cmd = [script, namelist, logfile]

    from subprocess import check_output, STDOUT
    try:
        check_output(cmd, stderr=STDOUT)
    except:
        logger.exception('esmvaltool failed!')
    return logfile

def diag_mydiag(
        credentials,
        project, models, variable, cmor_table, experiment, ensemble,
        start_year, end_year,
        output_format='ps',
        monitor=None):

    file_urls = retrieve_esgf_files(
        project=project, models=models, variable=variable, cmor_table=cmor_table, experiment=experiment, ensemble=ensemble,
        start_year=start_year, end_year=end_year,
        credentials=credentials,
        monitor=monitor)

    workspace = prepare_workspace(file_urls)

    namelist = generate_namelist(
        diag='mydiag',
        prefix=config.getConfigValue("hummingbird", "esmval_root"),
        workspace=workspace,
        models=models,
        cmor_table=cmor_table,
        experiment=experiment,
        ensemble=ensemble,
        variable=variable,
        start_year=start_year,
        end_year=end_year,
        output_format=output_format,
        )
    namelist_file = write_namelist(namelist=namelist, workspace=workspace)

    # run mydiag
    monitor("MyDiag ...", 10)
    log_file = esmvaltool(namelist=namelist_file)
    if logger.isEnabledFor(logging.DEBUG):
        with open(log_file, 'r') as f:
            logger.debug(f.read())
    monitor("MyDiag done", 90)

    # output: postscript
    import shutil
    out = 'output.ps'
    from os.path import join
    filename = 'MyDiag_MyVar.%s' % output_format
    shutil.copyfile(join(workspace, 'plots', 'MyDiag', filename), out)

    # references/acknowledgements document
    ack_file = join(workspace, 'work', 'namelist.txt')

    return out, namelist_file, log_file, ack_file
    
def diag_surfconplot(
        credentials,
        project, models, variable, cmor_table, experiment, ensemble,
        start_year, end_year,
        output_format='ps',
        monitor=None):
    file_urls = retrieve_esgf_files(
        project=project, models=models, variable=variable, cmor_table=cmor_table, experiment=experiment, ensemble=ensemble,
        start_year=start_year, end_year=end_year,
        credentials=credentials,
        monitor=monitor)

    workspace = prepare_workspace(file_urls)

    namelist = generate_namelist(
        diag='surfconplot',
        prefix=config.getConfigValue("hummingbird", "esmval_root"),
        workspace=workspace,
        models=models,
        cmor_table=cmor_table,
        experiment=experiment,
        ensemble=ensemble,
        variable=variable,
        start_year=start_year,
        end_year=end_year,
        output_format=output_format,
        )
    namelist_file = write_namelist(namelist=namelist, workspace=workspace)

    # run esmvaltool
    monitor("surfconplot ...", 10)
    log_file = esmvaltool(namelist=namelist_file)
    if logger.isEnabledFor(logging.DEBUG):
        with open(log_file, 'r') as f:
            logger.debug(f.read())
    monitor("surfconplot done", 90)

    # output: postscript
    import shutil
    out = 'output.ps'
    from os.path import join
    # TODO: fix output generation of esmvaltool
    filename = 'surfconplot_simple_%s_T2Ms_ANN.%s' % (variable, output_format)
    shutil.copyfile(join(workspace, 'plots', 'surfconplot_simple', filename), out)
    
    # references/acknowledgements document
    ack_file = join(workspace, 'work', 'namelist.txt')

    return out, namelist_file, log_file, ack_file

def diag_perfmetrics(
        credentials,
        project, models, variable, cmor_table, experiment, ensemble,
        start_year, end_year,
        output_format='ps',
        monitor=None):
    field_type = 'T3M'
    if variable in ['tas', 'rsut', 'rlut']:
        field_type = 'T2Ms'

    file_urls = retrieve_esgf_files(
        project=project, models=models, variable=variable, cmor_table=cmor_table, experiment=experiment, ensemble=ensemble,
        start_year=start_year, end_year=end_year,
        credentials=credentials,
        monitor=monitor)

    workspace = prepare_workspace(file_urls)

    namelist = generate_namelist(
        diag='perfmetrics',
        prefix=config.getConfigValue("hummingbird", "esmval_root"),
        workspace=workspace,
        models=models,
        cmor_table=cmor_table,
        experiment=experiment,
        ensemble=ensemble,
        variable=variable,
        start_year=start_year,
        end_year=end_year,
        output_format=output_format,
        )
    namelist_file = write_namelist(namelist=namelist, workspace=workspace)

    # run esmvaltool
    monitor("perfmetrics ...", 10)
    log_file = esmvaltool(namelist=namelist_file, prefix=prefix)
    if logger.isEnabledFor(logging.DEBUG):
        with open(log_file, 'r') as f:
            logger.debug(f.read())
    monitor("perfmetrics done", 90)

    # output: postscript
    import shutil
    out = 'output.ps'
    from os.path import join
    filename = 'namelist_%s-850_Globta-200_Glob_RMSD_grading.%s' % (variable, output_format)
    shutil.copyfile(join(workspace, 'plots', 'perfmetrics_grading', filename), out)

    # references/acknowledgements document
    ack_file = join(workspace, 'work', 'namelist.txt')

    return out, namelist_file, log_file, ack_file

def retrieve_esgf_files(
        project, models, variable, cmor_table, experiment, ensemble,
        start_year, end_year,
        distrib=True, replica=False, limit=100,
        credentials=None,
        monitor=None):
    from malleefowl.esgf.search import ESGSearch
    from malleefowl.download import download_files
    # TODO: configure archive_root only in malleefowl
    from os import environ
    if not environ.has_key('ESGF_ARCHIVE_ROOT'):
        environ['ESGF_ARCHIVE_ROOT'] = config.getConfigValue("hummingbird", "archive_root")

    # search
    constraints = []
    constraints.append( ("project", project ) )
    for model in models:
        constraints.append( ("model", model ) )
    constraints.append( ("variable", variable ) )
    constraints.append( ("cmor_table", cmor_table ) )
    constraints.append( ("experiment", experiment ) )
    constraints.append( ("ensemble", ensemble ) )

    logger.debug("constraints: %s", constraints)

    logger.info("esgsearch ...")
    esgsearch = ESGSearch(
        url = config.getConfigValue("hummingbird", "esgsearch_url"),
        distrib = distrib,
        replica = replica,
        latest = True,
        monitor = monitor,
    )

    (urls, summary, facet_counts) = esgsearch.search(
        constraints = constraints,
        query = "*:*",
        start = "%d-01-01" % start_year,
        end = "%d-12-31" % end_year,
        search_type = "File",
        limit = limit,
        offset = 0,
        temporal = False)
     
    # download
    logger.info("download ...")
    file_urls = download_files(
        urls = urls,
        credentials = credentials,
        monitor = monitor)
    return file_urls

def prepare_workspace(file_urls):
    logger.info("prepare workspace ...")
    # symlink files to workspace dir
    from urlparse import urlparse
    from os import mkdir,chmod, symlink
    from os.path import exists, basename, join, realpath, curdir, abspath
    workspace = abspath(join(curdir, 'workspace'))
    mkdir(workspace)
    # TODO: docker needs full access to create new files
    #import stat
    #chmod(workspace, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
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

def generate_namelist(prefix, workspace,
                      models, experiment, cmor_table, ensemble, variable,
                      start_year, end_year,
                      diag='mydiag',
                      output_format='ps'):
    logger.info("generate namelist: diag=%s", diag)

    namelist = 'namelist_simple.xml'
    if diag == 'perfmetrics':
        namelist = 'namelist_perfmetrics.xml'
        
    from os.path import join, dirname
    from mako.template import Template
    mytemplate = Template(
        filename=join(dirname(__file__), 'templates', namelist),
        output_encoding='utf-8',
        encoding_errors='replace')
    return mytemplate.render_unicode(
        diag=diag,
        prefix=prefix,
        workspace=workspace,
        obs_root=config.getConfigValue("hummingbird", "obs_root"),
        models=models,
        experiment=experiment,
        cmor_table=cmor_table,
        ensemble=ensemble,
        variable=variable,
        start_year=start_year,
        end_year=end_year,
        output_format=output_format
        )
   
def write_namelist(namelist, workspace):
    logger.debug(namelist)
    from os.path import join, abspath
    #from tempfile import mkstemp
    #_,outfile = mkstemp(prefix='namelist_', suffix='.xml', dir=curdir)
    outfile = abspath(join(workspace, "namelist.xml"))
    with open(outfile, 'w') as fp:
        fp.write(namelist)
    return outfile


