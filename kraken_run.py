import pandas as pd
import os, time, json, boto3, subprocess
import mysql.connector as sqlq
from dotenv import load_dotenv

load_dotenv()

USER = 'admin'
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')

metadata = {'USER':USER,'PASSWORD':PASSWORD,'HOST':HOST,'DATABASE':DATABASE}

def getFileFormat(sample_id, q, input_type, metadata):
	i_type = {input_type:input_type[:4].upper()}
	conn = sqlq.connect(user=metadata['USER'],password=metadata['PASSWORD'],host=metadata['HOST'],database=metadata['DATABASE'])
	cursor = conn.cursor()
	query = "SELECT fileName FROM files WHERE fileID = %s OR filePairKey = %s AND fileCode = '"+input_type[:4].upper()+"'"
	values = (sample_id, sample_id)
	cursor.execute(query, values)
	res = (cursor.fetchall())[0]
	conn.commit()
	cursor.close()
	return res[0]



def downloadfiles(s3, sample_id, q, input_bucket, input_prefix):
	if input_bucket=='prod-aai':
		first_filename=getFileFormat(sample_id, q, input_prefix.split('/')[0], metadata)
		if q==2:
			objects = s3.list_objects(Bucket='prod-aai', Prefix=input_prefix+'/')
			for obj in objects.get('Contents', []):
				key = obj['Key']
				if key.find('.json')==-1:
					# s3.download(obj.key, 'paired_samples/'+obj.key.split('/')[-1])
					s3.download_file('prod-aai', key, 'paired_samples/'+ key.split('/')[-1])
				else:
					# bucket.download_file(obj.key, obj.key.split('/')[-1])
					s3.download_file('prod-aai', key, key.split('/')[-1])
		elif q==1:
			s3.download_file('prod-aai',input_prefix+'/'+sample_id,'single_samples/'+sample_id)
		elif q==0:
			s3.download_file('prod-aai',input_prefix+'/'+sample_id,'single_samples/'+sample_id)
		is_fastq = rename_files(sample_id,q,first_filename)	

	else:
		if q==2:
			s3.download_file(input_bucket,input_prefix+'/'+sample_id+'_1.fastq.gz','paired_samples/'+sample_id+'_1.fastq.gz')
			s3.download_file(input_bucket,input_prefix+'/'+sample_id+'_2.fastq.gz','paired_samples/'+sample_id+'_2.fastq.gz')
		elif q==1:
			s3.download_file(input_bucket,input_prefix+'/'+sample_id+'.fastq.gz','single_samples/'+sample_id+'.fastq.gz')
		elif q==0:
			s3.download_file(input_bucket, input_prefix+'/'+sample_id+'.fastq.gz','single_samples/'+sample_id+'.fastq.gz')
	
		is_fastq = [True, '.fastq.gz']
	return is_fastq

def rename_files(sample_id,q,first_filename):
	is_fastq = True
	if ".fastq.gz" in first_filename:
		suff =  ".fastq.gz"
	elif ".gz" in first_filename:
		suff =  ".gz"
		is_fastq = False
	elif ".fastq" in first_filename:
		suff =  ".fastq"
	elif ".fq.gz" in first_filename:
		suff =  ".fq.gz"
	if q==2:
		jsd = json.load(open(sample_id+'.json'))
		os.rename('paired_samples/'+jsd['1'][0],'paired_samples/'+sample_id+'_1'+suff)
		os.rename('paired_samples/'+jsd['2'][0],'paired_samples/'+sample_id+'_2'+suff)
		if suff=='.fastq':
			for u in [sample_id+'_1'+suff,sample_id+'_2'+suff]:
				subprocess.call(['pigz','paired_samples/'+u])
				suff=".fastq.gz"
	else:
		# add real sample ids in future for single end
		os.rename('single_samples/'+sample_id,'single_samples/'+sample_id+suff)
		if suff=='.fastq':
			subprocess.call(['pigz','single_samples/'+sample_id+suff])
			suff=".fastq.gz"
	return [is_fastq, suff]
a = []

while True:
	k_dr = os.listdir('/home/kraken_db')
	json_f = [item for item in k_dr if '.json' in item]
	for a_json_f in json_f:
		if a_json_f not in a:
			sample_id = a_json_f.replace('.json','')
			s3 = boto3.client("s3",region_name='ap-south-1')
			input_dict = json.load(open('/home/kraken_db/'+a_json_f))
			q = int(input_dict['q'])
			# input_type = input_dict['input_type']
			input_bucket = input_dict['input_bucket']
			input_prefix = input_dict['input_prefix']
			fastq = downloadfiles(s3, sample_id, q, input_bucket, input_prefix)
			if q==2:
				bio_status1 = subprocess.call(['bash', 'mdd.sh', sample_id, sample_id+'_1'+fastq[1], sample_id+'_2'+fastq[1]])
			elif q==1 or q==0:
				bio_status1 = subprocess.call(['bash', 'mdd.sh', sample_id, sample_id+fastq[1]])
			a.append(a_json_f)

		else:
			time.sleep(10)
