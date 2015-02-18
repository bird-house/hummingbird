from os.path import join, dirname

from malleefowl import config
from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

from hummingbird.exceptions import ProcessError

from mako.lookup import TemplateLookup
mylookup = TemplateLookup(directories=[join(dirname(__file__), 'templates')],
                          output_encoding='utf-8', encoding_errors='replace')

def diag(
    name,
    credentials,
    constraints,
    start_year, end_year,
    output_format='ps',
    monitor=None):

    # TODO: maybe use result dict
    out = namelist = log_file = reference = None
    
    try:
        workspace = esgf_workspace(
            constraints=constraints,
            start_year=start_year, end_year=end_year,
            credentials=credentials,
            monitor=monitor)
        namelist = generate_namelist(
            diag=name,
            workspace=workspace,
            constraints=constraints,
            start_year=start_year,
            end_year=end_year,
            output_format=output_format,
            )

        # run diag
        monitor("%s ..." % name, 10)
        log_file = esmvaltool(namelist, workspace)
        monitor("%s done" % name, 90)

        # references/acknowledgements document
        reference = join(workspace, 'work', 'namelist.txt')

        # plot output
        out = find_plot(workspace, output_format)
    except:
        logger.exception("diag %s failed!", name)
        raise
    return out, namelist, log_file, reference

def esmvaltool(namelist, workspace):
    prefix = config.getConfigValue("hummingbird", "esmval_root")
    logger.info("run esmvaltool: prefix=%s", prefix)
    logger.debug("namelist=%s", namelist)

    # set ncl path
    ncarg_root = config.getConfigValue("hummingbird", "ncarg_root")
    from os import environ
    environ['NCARG_ROOT'] = ncarg_root.strip()
    environ['PATH'] = environ['NCARG_ROOT'] + '/bin' + ':' + environ['PATH']
    logger.debug('path with ncarg_root: %s', environ['PATH'])

    # build cmd
    from os.path import abspath
    script = join(prefix, "esmval.sh")
    log_file = abspath(join(workspace, 'log.txt'))
    cmd = [script, namelist, log_file]

    # run cmd
    from subprocess import check_output, STDOUT
    try:
        check_output(cmd, stderr=STDOUT)
    except:
        logger.exception('esmvaltool failed!')

    # debug: show logfile
    if logger.isEnabledFor(logging.DEBUG):
        with open(log_file, 'r') as f:
            logger.debug(f.read())
    
    return log_file

def build_constraints(project=None, models=[], variable=None, cmor_table=None, experiment=None, ensemble=None):
    from werkzeug.datastructures import MultiDict

    # search
    constraints = MultiDict()
    if project is not None:
        constraints.add("project", project)
    for model in models:
        constraints.add("model", model)
    if variable is not None:
        constraints.add("variable", variable)
    if cmor_table is not None:
        constraints.add("cmor_table", cmor_table)
    if experiment is not None:
        constraints.add("experiment", experiment)
    if ensemble is not None:
        constraints.add("ensemble", ensemble)

    logger.debug("constraints: %s", constraints)
    return constraints

def retrieve_esgf_files(
        constraints, start_year, end_year,
        distrib=True, replica=False, limit=100,
        credentials=None,
        monitor=None):
    from malleefowl.esgf.search import ESGSearch
    from malleefowl.download import download_files
    # TODO: configure archive_root only in malleefowl
    from os import environ
    if not environ.has_key('ESGF_ARCHIVE_ROOT'):
        environ['ESGF_ARCHIVE_ROOT'] = config.getConfigValue("hummingbird", "archive_root")

    logger.info("esgsearch ...")
    esgsearch = ESGSearch(
        url = config.getConfigValue("hummingbird", "esgsearch_url"),
        distrib = distrib,
        replica = replica,
        latest = True,
        monitor = monitor,
    )

    (urls, summary, facet_counts) = esgsearch.search(
        constraints = [kv for kv in constraints.iteritems(multi=True)],
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
    from os.path import exists, basename, realpath, curdir, abspath
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

def esgf_workspace(
        constraints,
        start_year, end_year,
        credentials,
        monitor=None):
    file_urls = retrieve_esgf_files(
        constraints=constraints,
        start_year=start_year, end_year=end_year,
        credentials=credentials,
        monitor=monitor)

    return prepare_workspace(file_urls)

def generate_namelist(diag, workspace,
                      constraints,
                      start_year, end_year,
                      output_format='ps'):
    logger.info("generate namelist: diag=%s", diag)

    namelist = 'namelist_%s.xml' % diag
    logger.debug("using namelist %s", namelist)
        
    mytemplate = mylookup.get_template(namelist)
    rendered_namelist = mytemplate.render_unicode(
        diag=diag,
        prefix=config.getConfigValue("hummingbird", "esmval_root"),
        workspace=workspace,
        obs_root=config.getConfigValue("hummingbird", "obs_root"),
        constraints=constraints,
        start_year=start_year,
        end_year=end_year,
        output_format=output_format
        )
    return write_namelist(namelist=rendered_namelist, workspace=workspace)
   
def write_namelist(namelist, workspace):
    logger.debug(namelist)
    from os.path import abspath
    outfile = abspath(join(workspace, "namelist.xml"))
    with open(outfile, 'w') as fp:
        fp.write(namelist)
    return outfile

def find_plot(workspace, output_format):
    import glob
    matches = glob.glob(join(workspace, 'plots', '*', '*.%s' % output_format))
    if len(matches) == 0:
        raise ProcessError("no result plot found in workspace/plots")
    elif len(matches) > 1:
        raise ProcessError("more then one plot found %s", matches)
    logger.info("plot file=%s", matches[0])
    return matches[0]




