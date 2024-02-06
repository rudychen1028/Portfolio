#!/home/hadoop/chihwei/zeekArchive/zeekarchive/bin/python3
import gzat
from gzat import log_to_sparkdf
from gzat.log_to_dataframe import LogToDataFrame

from pyspark.sql import functions as F
from pyspark.sql import SparkSession, DataFrame

import glob, os, pdb, time, sys
import datetime, pyhdfs, argparse
import pandas as pd

from functools import reduce

class Preprocess:
    def __init__(self, zeekPath, fileDate, dst_folder, metric=None):
        """
        Description:
                Create soft link to avoid illegal file name
        Input:
                zeekPath   : Local zeek file path
                fileDate   : Target file date
                dst_folder : Soft link dst path
                metric     : Zeek metric name (http.00:00:00-01:00:00.log.gz -> http)
        """
        self.zeekPath = zeekPath
        self.fileDate = fileDate
        self.dst_folder = dst_folder
        self.metric = metric

        self.files = self._get_files() # Get file list
    def _get_files(self):
        """
        Output:
                output: file list
        """
        if self.metric != None:
            path = f"{self.zeekPath}/{self.fileDate}/{self.metric}.*"
        else:
            path = f"{self.zeekPath}/{self.fileDate}/*"
        files = glob.glob(path)
        output = list()
        for tfile in files:
            output.append(tfile)
        return output
    def _create_folder(self):
        """
        Description:
                If target folder not exist, then create folder
        """
        path = f"{self.dst_folder}/{self.fileDate}"
        if not os.path.isdir(path):
            print(f"Path : {path} not exist")
            print(f"Create {path}")
            os.mkdir(path)
    def _create_link(self, src, dst):
        """
        Description:
                If target link not exist, then create link
        """
        try:
            os.symlink(src, dst)
            print(f"Finish create create link : {dst}")
        except: pass
    def get_new_files(self):
        """
        Output:
                output: Get links
        """
        self._create_folder()
        output = list()
        for tfile in self.files:
            zeek_file = tfile.split('/')[-1].replace(':','.')
            newfilepath = f"{self.dst_folder}/{self.fileDate}/{zeek_file}"
            self._create_link(tfile, newfilepath)
            output.append(newfilepath)
        return output

class ZeekReader:
    def __init__(self, spark, files):
        """
        Input:
                spark   : Spark Session
                files   : Zeek file list (array-like or iterable data)
        """
        files_info = pd.DataFrame({"files":files})
        files_info['metric'] = files_info['files'].apply(lambda x: x.split('/')[-1].split('.')[0])

        self.files_info = files_info
        self.spark_it = log_to_sparkdf.LogToSparkDF(spark)

    def _read_zeek_to_sparkdf(self, metric, files):
        """
        Input:
                metric  : Metric name
                files   : Target file list (array-like or iterable data)
        Output:
                spdf    : DataFrame
        """
        def _reformat(partition):
            """
            Description:
                Reformat labeling metric name into zeek data
            """
            keys = list()
            for row in partition:
                row = row.asDict()
                if len(keys) == 0:
                    keys = list(row.keys())
                if 'ts' in keys:
                    row['ts'] = row['ts'].strftime('%Y-%m-%d %H:%M:%S')
                yield {'metric':metric, 'data':row}

        spdf_list = list()
        for tfile in files:
            spdf_list.append(self.spark_it.create_dataframe(tfile))
        o_rdd = reduce(DataFrame.unionAll, spdf_list).rdd
        spdf = o_rdd.mapPartitions(_reformat).toDF()
        return spdf

    def readAllData(self):
        """
        Description:
                Read all Zeek data into one dataframe
        """
        zeek_data = list()
        for metric, info in self.files_info.groupby('metric'):
            if metric in ["conn-summary", "stderr", "stdout"]: continue
            print(f'Reading {metric}')
            files = info.files.tolist()
            res = self._read_zeek_to_sparkdf(metric, files)
            zeek_data.append(res)
        return reduce(DataFrame.unionAll, zeek_data)

class ZeekDataUploader:
    def __init__(self, fileDate, spdf, hdfs_root, compress=None):
        """
        Input
                fileDate        : zeek logs file date
                spdf            : zeek data in spark dataframe
                hdfs_root       : hdfs root path, hdfs://[NameNode]:[Port/]/ , like hdfs://202.140.186.94:9000/
        """
        self.fileDate = fileDate
        self.spdf = spdf
        self.hdfs_root = hdfs_root
        self.compress = compress
        self.tmp_hdfs_dir = f"{self.hdfs_root}/tmp/zeek"
    def uploadTemporary_GetPartitionNum(self, spark):
        """
        Description:
                Analysis data size and number of files to cut
        Input:
                spark   : Spark Session
        Output:
                fileNum : split file number
        """
        print("Get partition number and dir size")
        if self.compress != None:
            self.spdf.write.mode('overwrite').format("orc").option('compression', self.compress).save(self.tmp_hdfs_dir)
        else:
            self.spdf.write.mode('overwrite').format("orc").save(self.tmp_hdfs_dir)

        hadoop = spark._jvm.org.apache.hadoop

        fs = hadoop.fs.FileSystem
        conf = hadoop.conf.Configuration()
        conf.set("fs.defaultFS", self.hdfs_root)
        path = hadoop.fs.Path(self.tmp_hdfs_dir)
        dirSize = fs.get(conf).getContentSummary(path).getSpaceConsumed()#//(3*128*1024*1024) + 1
        print(f"Dir size: {dirSize/(3*1024*1024):.2f} MB")
        #tmp = dirSize//(3*128*1024*1024)
        black_size = 256
        R = 2
        tmp = (dirSize*R)//(3*black_size*1024*1024)
        if tmp == 0:
           fileNum = 1
        else:
           fileNum = tmp + 2
           #fileNum = tmp + 1
        print(f'Split data into {fileNum} partitions')
        return int(fileNum)
    def saveToORC(self):
        self.spdf.write.mode('overwrite').format("orc").option('compression','snappy').save(self.tmp_hdfs_dir)

    def startUpload(self, fileNum=24):
        """
        Description:
                Upload Zeek data into target dir path
        Input:
                fileNum : Default = 24
        """
        path = f"{self.hdfs_root}/zeek/{self.fileDate}"
        print(f"Upload {self.fileDate} data to hadoop: {path}")
        print(f"compression mode : {self.compress}")
        if self.compress != None:
            self.spdf.repartition(fileNum).write.mode('overwrite').format("orc").option('compression','snappy').save(path)
        else:
            self.spdf.repartition(fileNum).write.mode('overwrite').format("orc").save(path)

def check_nameNode():
    client = pyhdfs.HdfsClient(hosts=['202.140.186.206', '202.140.186.94'], user_name="hadoop")
    #client = pyhdfs.HdfsClient(hosts=['202.169.169.27', '202.169.169.39'], user_name="hadoop")
    try:
        res = client.get_active_namenode()
        return res.replace('50070', '9000')
    except pyhdfs.HdfsNoServerException:
        return None

def check_safe_mode(spark, nameNode):
    sc            = spark.sparkContext
    URI           = sc._gateway.jvm.java.net.URI
    FileSystem    = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
    Configuration = sc._gateway.jvm.org.apache.hadoop.conf.Configuration
    fs = FileSystem.get(URI(f"hdfs://{nameNode}"), Configuration())
    return fs.isInSafeMode()

def Zeek_archive(fileDate=datetime.datetime.now().strftime('%Y-$m-%d'), compress="zlib"):
    # check nameNode aviable or not
    nameNode = check_nameNode()
    hdfs = f"hdfs://{nameNode}"

    if nameNode == None:
        print("No NameNode avaiable !!")
        sys.exit(1)
    print(f"Current NameNode : {nameNode}")

    # Create Spark Session
    spark = SparkSession.builder\
                .master("local[20]")\
                .appName('archive zeek data to hadoop')\
                .config("spark.debug.maxToStringFields", 1000)\
                .config('spark.driver.memory','20g')\
                .config('spark.driver.maxResultSize', '10g')\
                .config("spark.sql.execution.arrow.pyspark.enabled", "true")\
                .getOrCreate()
    spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

    # check nameNode is in safe mode or not
    if check_safe_mode(spark, nameNode):
        print(f"NameNode {nameNode} is in Safe Mode, not writable")
        sys.exit(2)


    zeekPath = "/zeek"
    dst_folder = "/home/hadoop/chihwei/zeekArchive/process"

    metric = "*"
    hdfs_root = f"{hdfs}"

    print(f"Start processing Zeek data: {zeekPath}/{fileDate}/{metric}")

    pre_procress = Preprocess(zeekPath, fileDate, dst_folder, metric=metric)
    processing_files = pre_procress.get_new_files()


    zreader = ZeekReader(spark, processing_files)
    spdf = zreader.readAllData()

    zd_uploader = ZeekDataUploader(fileDate=fileDate, spdf=spdf, hdfs_root=hdfs_root, compress=compress)
    fileNum = zd_uploader.uploadTemporary_GetPartitionNum(spark)

    if compress!=None:
        zd_uploader.startUpload(fileNum)

def valid_date(target):
    try:
        datetime.datetime.strptime(target, "%Y-%m-%d")
        return target
    except ValueError:
        msg = "Not a valid date: {0!r}, use YYYY-mm-dd".format(target)
        raise argparse.ArgumentTypeError(msg)

def date_reformat(target):
    try:
        return datetime.datetime.strptime(target, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0!r}, use YYYY-mm-dd".format(target)
        raise argparse.ArgumentTypeError(msg)

def get_command():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--date', type=valid_date, help="--date [YYYY-mm-dd]")
    parser.add_argument('-s', '--stime', type=date_reformat, help="--stime [YYYY-mm-dd]")
    parser.add_argument('-e', '--etime', type=date_reformat, help="--etime [YYYY-mm-dd]")
    parser.add_argument('-c', '--compress', type=str, default='zlib', help="--compress zlib")
    return parser

def daterange(stime, etime):
    """
    Description:
        Generator to loop datetime type
    Input:
        stime: datetime type
        etime: datetime type
    Output:
        -> yield string (YYYY-mm-dd)
    """
    days = int((etime-stime).days) + 1
    for d in range(days):
        output = stime + datetime.timedelta(d)
        yield output.strftime('%Y-%m-%d')

if __name__ == "__main__":

    parser = get_command()
    if parser.parse_args().date:
        #Zeek_archive(parser.parse_args().date, compress=None)
        Zeek_archive(parser.parse_args().date, compress=parser.parse_args().compress)
    elif parser.parse_args().stime and parser.parse_args().etime:
        stime = parser.parse_args().stime
        etime = parser.parse_args().etime
        for fileDate in daterange(stime, etime):
            try:
                Zeek_archive(fileDate)
            except Exception as e:
                print(f"Processing {fileDate} faill!!")
                print(f"Caused By {e}")
    else:
        parser.print_help()
