from malleefowl.process import WPSProcess
from malleefowl import config

from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

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
            default = False,
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
            default="MPI-ESM-LR",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["ACCESS1-0", "ACCESS1-3", "CMCC-CMS", "CanCM4", "EC-EARTH", "GFDL-CM2.1", "IPSL-CM5A-LR", "IPSL-CM5A-MR", "IPSL-CM5B-LR", "MPI-ESM-LR", "MPI-ESM-MR", "MPI-ESM-P"]
            )

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            default="ta",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
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

        self.namelist = self.addComplexOutput(
            identifier="namelist",
            title="namelist",
            abstract="",
            formats=[{"mimeType":"application/xml"}],
            asReference=True,
            )

        self.summary = self.addComplexOutput(
            identifier="summary",
            title="summary",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting", 0)

        # TODO: configure archive_root only in malleefowl
        from os import environ
        if not environ.has_key('ESGF_ARCHIVE_ROOT'):
            environ['ESGF_ARCHIVE_ROOT'] = config.getConfigValue("hummingbird", "archive_root")

        # search
        constraints = []
        constraints.append( ("project", "CMIP5" ) )
        constraints.append( ("model", self.model.getValue() ) )
        constraints.append( ("variable", self.variable.getValue() ) )
        constraints.append( ("cmor_table", self.cmor_table.getValue() ) )
        constraints.append( ("experiment", self.experiment.getValue() ) )
        constraints.append( ("ensemble", self.ensemble.getValue() ) )

        self.show_status("search", 5)
        urls = esmvaltool.search(
            url = config.getConfigValue("hummingbird", "esgsearch_url"),
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
        file_urls = esmvaltool.download(
            urls = urls,
            credentials = self.credentials.getValue(),
            monitor=self.show_status)

        # prepare workspace dir
        self.show_status("prepare", 10)
        workspace_dir = esmvaltool.prepare(file_urls)

        # generate namelist
        #prefix = "/home/esmval/esmvaltool"
        prefix = "/home/pingu/sandbox/esmvaltool-git-svn"
        namelist = esmvaltool.generate_namelist(
            name="MyDiag",
            prefix=prefix,
            #workspace="/workspace",
            workspace=workspace_dir,
            model=self.model.getValue(),
            cmor_table=self.cmor_table.getValue(),
            experiment=self.experiment.getValue(),
            ensemble=self.ensemble.getValue(),
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            )
        f_namelist = esmvaltool.write_namelist(name="MyDiag", namelist=namelist)
        self.namelist.setValue(f_namelist)

        # run esmvaltool
        self.show_status("esmvaltool started", 20)
        #log_file = esmvaltool.esmval_docker(f_namelist)
        log_file = esmvaltool.esmval_console(prefix, f_namelist)
        self.summary.setValue( log_file )
        self.show_status("esmvaltool done", 100)

        # output: postscript
        # TODO: permisson problem with generated files within docker container
        import shutil
        out = 'output.ps'
        from os.path import join
        shutil.copyfile(join(workspace_dir, 'plots', 'MyDiag', 'MyDiag_MyVar.ps'), out)
        self.output.setValue(out)
        

 
