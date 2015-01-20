import os

from malleefowl.process import WPSProcess
from malleefowl import config

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

def search(distrib, replica, limit, constraints, start_year, end_year, monitor):
    from malleefowl.esgf.search import ESGSearch
    esgsearch = ESGSearch(
        url = "http://localhost:8081/esg-search",
        distrib = distrib,
        replica = replica,
        latest = True,
        monitor = monitor,
    )

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
    # TODO: dont use hard coded path
    #from os import environ
    #if not environ.has_key('ESGF_ARCHIVE_ROOT'):
    #    environ['ESGF_ARCHIVE_ROOT'] = "/gpfs_750/projects/CMIP5/data"
    file_urls = download_files(
        urls = urls,
        credentials = credentials,
        monitor = monitor)
    return file_urls

def prepare(file_urls):
    # symlink files to data dir
    from urlparse import urlparse
    from os import mkdir,chmod
    from os.path import exists, basename, join, realpath
    data_dir = 'data'
    mkdir(data_dir)
    # TODO: docker needs full access to create new files
    import stat
    chmod(data_dir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
    input_dir = join('data', 'input-data')
    mkdir(input_dir)
    results = []
    for url in file_urls:
        filename = realpath(urlparse(url).path)
        logger.debug('filename = %s', filename)
        if exists(filename):
            new_name = join(input_dir, basename(filename))
            # TODO: make sure symlinks work in docker container
            logger.debug("new name: %s", new_name)
            os.symlink(filename, new_name)
            results.append(new_name)
    return data_dir

def esmvaltool():
    from os.path import abspath, curdir, join, realpath
    mountpoint = "%s:/data" % abspath(join(curdir, 'data'))
    cmd = ["docker", "run", "--rm"]
    cmd.extend([ "-v", mountpoint])
    # archive path
    for archive in config.archive_root():
        cmd.extend(["-v", "%s:%s:ro" % (archive, archive)])
    # cache path
    cache_path = realpath(config.cache_path())
    cmd.extend(["-v", "%s:%s:ro" % (cache_path, cache_path)])
    cmd.extend(["-t", "birdhouse/esmvaltool"])

    from subprocess import check_call
    try:
        # TODO: dont use hard coded path
        check_call(cmd)
    except:
        logger.exception('docker failed')
        import time
        time.sleep(60)

class ESMValToolProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "esmvaltool",
            title = "ESMValTool",
            version = "0.1",
            abstract="Test Process for ESMValTool")

        self.credentials = self.addComplexInput(
            identifier = "credentials",
            title = "X509 Certificate",
            abstract = "X509 proxy certificate to access ESGF data.",
            minOccurs=0,
            maxOccurs=1,
            maxmegabites=1,
            formats=[{"mimeType":"application/x-pkcs7-mime"}],
            )

        self.distrib = self.addLiteralInput(
            identifier = "distrib",
            title = "Distributed",
            abstract = "If flag is set then a distributed search will be run.",
            default = True,
            minOccurs=1,
            maxOccurs=1,
            type=type(True)
            )

        self.replica = self.addLiteralInput(
            identifier = "replica",
            title = "Replica",
            abstract = "If flag is set then search will include replicated datasets.",
            default = False,
            minOccurs=1,
            maxOccurs=1,
            type=type(True)
            )

        self.limit = self.addLiteralInput(
            identifier = "limit",
            title = "Limit",
            abstract = "Maximum number of datasets in search result",
            default = 20,
            minOccurs=1,
            maxOccurs=1,
            type=type(1),
            allowedValues=[0,1,2,5,10,20,50,100,200]
            )

        self.model = self.addLiteralInput(
            identifier="model",
            title="Model",
            abstract="",
            default="IPSL-CM5A-MR",
            type=type(''),
            minOccurs=1,
            maxOccurs=10,
            allowedValues=["ACCESS1-0", "ACCESS1-3", "CMCC-CMS", "CanCM4", "EC-EARTH", "GFDL-CM2.1", "IPSL-CM5A-LR", "IPSL-CM5A-MR", "IPSL-CM5B-LR", "MPI-ESM-LR"]
            )

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            default="tas",
            type=type(''),
            minOccurs=1,
            maxOccurs=10,
            allowedValues=['ta', 'tas', 'ua', 'va', 'zg', 'pr', 'rlut', 'rsut']
            )

        self.cmor_table = self.addLiteralInput(
            identifier="cmor_table",
            title="CMOR Table",
            abstract="",
            default="Amon",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['Amon']
            )

        self.experiment = self.addLiteralInput(
            identifier="experiment",
            title="Experiment",
            abstract="",
            default="historical",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['historical']
            )

        self.ensemble = self.addLiteralInput(
            identifier="ensemble",
            title="Ensemble",
            abstract="",
            default="r1i1p1",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['r1i1p1']
            )

        self.start_year = self.addLiteralInput(
            identifier="start_year",
            title="Start Year",
            abstract="",
            default="2001",
            type=type(2001),
            minOccurs=1,
            maxOccurs=1
            )

        self.end_year = self.addLiteralInput(
            identifier="end_year",
            title="End Year",
            abstract="",
            default="2005",
            type=type(2005),
            minOccurs=1,
            maxOccurs=1
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="output",
            abstract="",
            formats=[{"mimeType":"application/postscript"}],
            asReference=True,
            )

        self.summary = self.addComplexOutput(
            identifier="summary",
            title="summary",
            abstract="",
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting", 0)

        # search
        constraints = []
        constraints.append( ("project", "CMIP5" ) )
        for model in self.getInputValues(identifier='model'):
            constraints.append( ("model", model ) )
        for variable in self.getInputValues(identifier='variable'):
            constraints.append( ("variable", variable ) )
        constraints.append( ("cmor_table", self.cmor_table.getValue() ) )
        constraints.append( ("experiment", self.experiment.getValue() ) )
        constraints.append( ("ensemble", self.ensemble.getValue() ) )

        self.show_status("search", 5)
        urls = search(
            distrib=self.distrib.getValue(),
            replica=self.replica.getValue(),
            limit=self.limit.getValue(),
            constraints=constraints,
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            monitor=self.show_status
            )
        
        # download
        self.show_status("download", 10)
        file_urls = download(
            urls = urls,
            credentials = self.credentials.getValue(),
            monitor=self.show_status)

        # symlink files to data dir
        self.show_status("prepare", 10)
        data_dir = prepare(file_urls)

        # run esmvaltool
        self.show_status("esmvaltool started", 20)
        esmvaltool()
        self.show_status("esmvaltool done", 100)

        # output: postscript
        # TODO: permisson problem with generated files within docker container
        import shutil
        out = 'output.ps'
        from os.path import join
        shutil.copyfile(join(data_dir, 'plots', 'MyDiag', 'MyDiag_MyVar.ps'), out)
        self.output.setValue(out)
        
        # output: summary
        import json
        outfile = self.mktempfile(suffix='.json')
        with open(outfile, 'w') as fp:
            json.dump(obj=file_urls, fp=fp, indent=4, sort_keys=True)
            self.summary.setValue( outfile )

 
