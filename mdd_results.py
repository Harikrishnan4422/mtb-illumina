import os, pickle, subprocess, multiprocessing, re, boto3, time, requests, json, sys
import mysql.connector as sqlq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')



def get_max_time(s3, sample_id, completetime, links, input_type):
	ref={0:'nanopore/'+sample_id,1:'single/'+sample_id,2:'paired/'+sample_id+'/'+sample_id+'.json'}
	result_f = {'mcd':'.xlsx'}
	if links=='pro':
		uploaded_file = s3.list_objects_v2(Bucket='webserver-deployment', Prefix=input_type+'/'+ref[q])
	else:
		uploaded_file = s3.list_objects_v2(Bucket='webserver-deployment', Prefix='retries/'+links)
	all_time=[]
	for k,v in result_f.items():
		a_file = s3.list_objects_v2(Bucket='webserver-deployment', Prefix=input_type+'/results/'+k+'/'+sample_id+v)
		if 'Contents' in a_file:
			all_time.append(abs(int((a_file['Contents'][0]['LastModified']-uploaded_file['Contents'][0]['LastModified']).total_seconds())))
	if len(all_time)>1 and max(all_time) > completetime:
		completetime = max(all_time)
	return completetime

def file_query(s3, sample_id, start_time, q, input_type, metadata, links):
	# i_type = {'nnaapipeline':'NNAA'}
	# flag='ERR'
	# qlis = ['DST', 'QCR']
	id_type = 'filePairKey'
	if q == 1 or q==0:
		id_type = 'fileID'
	# if p_type=='nnaapipeline':
	# 	botresponse = requests.get('http://10.10.20.150:80?files='+sample_id+'&type=mcd&state=err&code='+i_type[input_type].lower())
		
	completetime = int(time.time()-start_time)
	completetime = get_max_time(s3, sample_id, completetime, links,input_type)
	conn = sqlq.connect(user=metadata['USER'],password=metadata['PASSWORD'],host=metadata['HOST'],database=metadata['DATABASE'])
	cursor = conn.cursor()
	query = "UPDATE files SET completetime = %s WHERE "+id_type+"= %s AND fileCode = '"+input_type[:4].upper()+"'"
	values = (completetime, sample_id)
	cursor.execute(query, values)
	conn.commit()
	cursor.close()

def getFileFormat(sample_id, q, input_type,metadata):
	i_type = {'nnaapipeline':'NNAA'}
	conn = sqlq.connect(user=metadata['USER'],password=metadata['PASSWORD'],host=metadata['HOST'],database=metadata['DATABASE'])
	cursor = conn.cursor()
	query = "SELECT fileName FROM files WHERE fileID = %s OR filePairKey = %s AND fileCode = '"+i_type[input_type]+"'"
	values = (sample_id, sample_id)
	cursor.execute(query, values)
	res = (cursor.fetchall())[0]
	conn.commit()
	cursor.close()
	return res[0]

def downloadfiles(s3, sample_id, q, input_type,metadata):
	first_filename=getFileFormat(sample_id, q, input_type,metadata)
	if q==2:
		s3_resource = boto3.resource('s3')
		bucket = s3_resource.Bucket('webserver-deployment') 
		for obj in bucket.objects.filter(Prefix = input_type+'/paired/'+sample_id):
			if obj.key.find('.json')==-1:
				bucket.download_file(obj.key, 'paired_samples/'+obj.key.split('/')[-1])
			else:
				bucket.download_file(obj.key, obj.key.split('/')[-1])
	elif q==1:
		s3.download_file('webserver-deployment',input_type+'/single/'+sample_id,'single_samples/'+sample_id)
	is_fastq = rename_files(sample_id,q,first_filename)
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
	if q==2:
		jsd = json.load(open(sample_id+'.json'))
		os.rename('paired_samples/'+jsd['1'][0],'paired_samples/'+jsd['1'][1])
		os.rename('paired_samples/'+jsd['2'][0],'paired_samples/'+jsd['2'][1])
		if suff=='.fastq':
			for u in [sample_id+'_1'+suff,sample_id+'_2'+suff]:
				subprocess.call(['pigz','paired_samples/'+u])
	else:
		# add real sample ids in future for single end
		os.rename('single_samples/'+sample_id,'single_samples/'+sample_id+suff)
		if suff=='.fastq':
			subprocess.call(['pigz','single_samples/'+sample_id+suff])
	return is_fastq

def UpdateFileByMddPipeline(fileID, fileCode, status_, input_type):
	if fileCode.lower()!='nnaa' and input_type=='nnaapipeline':
		conn = sqlq.connect(user=metadata['USER'],password=metadata['PASSWORD'],host=metadata['HOST'],database=metadata['DATABASE'])
		cursor = conn.cursor()
		if fileCode.lower() == 'tbwg':
			query = "UPDATE files SET fileCode = 'TBWG', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'tbtr':
			query = "UPDATE files SET fileCode = 'TBTR', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'hiv1':
			query = "UPDATE files SET fileCode = 'HIV1', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'hiv2':
			query = "UPDATE files SET fileCode = 'HIV2', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'gono':
			query = "UPDATE files SET fileCode = 'GONO', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'cant':
			query = "UPDATE files SET fileCode = 'CANT', DSTFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'cana':
			query = "UPDATE files SET fileCode = 'CANA', DSTFlag = 'PRO', VIRFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		elif fileCode.lower() == 'covd':
			query = "UPDATE files SET fileCode = 'COVD', VDRFlag = 'PRO', QCFlag = 'PRO', COLFlag = 'PRO' WHERE (fileID = %s OR filePairKey = %s)"
		values = (fileID, fileID)
		cursor.execute(query, values)
		conn.commit()
		cursor.close()
	if input_type!='nnaapipeline':
		fileCode = input_type[:4]
	botresponse = requests.get('http://10.10.20.150:80?files='+fileID+'&type=mcd&state='+status_.lower()+'&code='+fileCode.lower())

def move_seq_files(s3, sample_id, q, dest, status_, input_type):
	seq_type = {0:'nanopore/',1:'single/',2:'paired/'}

	try:
		if input_type!='nnaapipeline':
			dest = input_type
		s3.upload_file(sample_id+'_kraken.txt','webserver-deployment',dest+'/results/mcd/'+sample_id+'-1.txt')
		s3.upload_file(sample_id+'_tophit.txt','webserver-deployment',dest+'/results/mcd/'+sample_id+'-2.txt')
		s3.upload_file(sample_id+'histogram.png','webserver-deployment',dest+'/results/mcd/'+sample_id+'.png')
		s3.upload_file(sample_id,'webserver-deployment-data','nnaapipeline/kraken/'+sample_id)
	except:
		status_="ERR"
	
	if dest!='nnaapipeline' and input_type=='nnaapipeline':
		# set the source and destination paths
		src_path = 'nnaapipeline/'+seq_type[q]
		dst_path = dest+'/'+seq_type[q]
		if q==2:
			src_path = 'nnaapipeline/'+seq_type[q]+sample_id+'/'
			dst_path = dest+'/'+seq_type[q]+sample_id+'/'


		# list all objects in the source path
		objects = s3.list_objects_v2(Bucket='webserver-deployment', Prefix=src_path)

		# create a list of objects to be moved
		objects_to_move = [{'Key': obj['Key']} for obj in objects.get('Contents', [])]

		# copy objects to the destination path
		for obj in objects_to_move:
			s3.copy_object(Bucket='webserver-deployment', CopySource={'Bucket': 'webserver-deployment', 'Key': obj['Key']}, Key=dst_path + obj['Key'].replace(src_path, ''))

		# delete objects from the source path
		for obj in objects_to_move:
			s3.delete_object(Bucket='webserver-deployment', Key=obj['Key'])

	UpdateFileByMddPipeline(sample_id, dest[:4].upper(), status_, input_type)

def generate_file(sample_id, q, metadata, links, input_type):
	eqn = len(os.listdir('queue'))
	# try:
	if eqn<=1:
	# try:
		with open('queue/'+sample_id+'.txt', 'w') as fp:
			pass
		status_="COM"
		start_time = time.time()
		s3 = boto3.client("s3",region_name='ap-south-1')
		with open('/data/kraken_db/'+sample_id+'.json', 'w') as f:
			json.dump({'q':str(q),'input_type':input_type}, f)
		# fastq = downloadfiles(s3, sample_id, q, input_type,metadata)
		cr_loop = True
		while cr_loop:
			if sample_id in os.listdir('/data/kraken_db'):
				cr_loop=False
			else:
				print('Waiting for sample to process..')
				time.sleep(10)
				if time.time()-start_time>2700:
					print('Took more time, exiting...')
					status_="ERR"
					break
		p_type = 'nnaapipeline'
		if status_=="COM":
			if q==2:
				bio_status1 = subprocess.call(['bash', 'mdd.sh', sample_id, sample_id+'_1.fastq.gz', sample_id+'_2.fastq.gz'])
			elif q==1 or q==0:
				bio_status1 = subprocess.call(['bash', 'mdd.sh', sample_id, sample_id+'.fastq.gz'])
			print(bio_status1)
			if bio_status1==0:
				df = pd.read_csv(sample_id+'_tophit.txt', sep='\t').sort_values(['Read Density(%)'],ascending=False)
				print(df)
				sp_names = list(df['Organism Name'].str.lower())
				
				for sp_name in sp_names:
					if sp_name.find('mycobacterium tuberculosis')!=-1:
						p_type = 'tbwgpipeline'
						if input_type == 'tbtrpipeline':
							p_type = 'tbtrpipeline'
						break
					elif sp_name.find('severe acute')!=-1:
						p_type = 'covdpipeline'
						break
					elif sp_name.find('neisseria gonorrhoeae')!=-1:
						p_type = 'gonopipeline'
						break
					elif sp_name.find('human immunodeficiency virus 1')!=-1:
						p_type = 'hiv1pipeline'
						break
					elif sp_name.find('human immunodeficiency virus 2')!=-1:
						p_type = 'hiv2pipeline'
						break
					elif sp_name.find('candida auris')!=-1:
						p_type = 'canapipeline'
						break
					elif sp_name.find('candida tropicalis')!=-1:
						p_type = 'cantpipeline'
						break
		print(p_type)
		file_query(s3, sample_id, start_time, q, input_type, metadata, links)
		move_seq_files(s3, sample_id,q, p_type, status_, input_type)

metadata = {'USER':USER,'PASSWORD':PASSWORD,'HOST':HOST,'DATABASE':DATABASE}

if __name__ == '__main__':
	sample_id=sys.argv[3]
	input_type=sys.argv[4]
	q=int(sys.argv[5])
	env=sys.argv[6]
	generate_file(sample_id, q, metadata, env,input_type)
