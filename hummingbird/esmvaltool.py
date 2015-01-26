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
    workspace_dir = abspath(join(curdir, 'workspace'))
    mkdir(workspace_dir)
    # TODO: docker needs full access to create new files
    import stat
    chmod(workspace_dir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
    input_dir = join(workspace_dir, 'input-data')
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
    return workspace_dir

def generate_namelist(name, prefix, workspace, model, experiment, cmor_table, ensemble, start_year, end_year):
    logger.info("generate namelist %s", name)
    
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
   
def write_namelist(name, namelist):
    from os import curdir
    #from tempfile import mkstemp
    #_,outfile = mkstemp(prefix='namelist_', suffix='.xml', dir=curdir)
    outfile = 'namelist_%s.xml' % name
    logger.info("namelist=%s", outfile)
    with open(outfile, 'w') as fp:
        fp.write(namelist)
    return outfile

def esmvaltool_console(namelist):
    from os import chdir
    from os.path import join, curdir, abspath
    mydir = abspath(join(curdir))
    logfile = join(mydir, 'log.txt')
    chdir("/home/pingu/sandbox/esmvaltool-git-svn")
    cmd = ["python", "main.py", "nml/namelist_MyDiag_generated.xml"]
    cmd.extend( [">", logfile] ) 

    from subprocess import check_call
    try:
        check_call(cmd)
    except:
        logger.exception('esmvaltool failed')
        #import time
        #time.sleep(60)
    finally:
        chdir(mydir)
    return logfile

def esmvaltool_docker(namelist):
    from os.path import abspath, curdir, join, realpath
    mountpoint = "%s:/workspace" % abspath(join(curdir, 'workspace'))
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
    # mount namelist
    cmd.extend(["-v", "%s:/home/esmval/esmvaltool/nml/namelist_MyDiag_generated.xml" % realpath(namelist)])
    cmd.extend(["birdhouse/esmvaltool"])

    from subprocess import check_call
    try:
        check_call(cmd)
    except:
        logger.exception('docker failed')
        #import time
        #time.sleep(60)
    return join(curdir, 'workspace', 'log.txt')

