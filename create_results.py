import os, pickle, subprocess, xlsxwriter, multiprocessing, boto3, time, requests, json, random
from flask import Flask, request, Response
import mysql.connector as sqlq
import pandas as pd

def create_excel(sample_id,i_df):
	writer = pd.ExcelWriter(os.path.join('excel_results',str(sample_id+'.xlsx')), engine='xlsxwriter')
	i_df.to_excel(writer, sheet_name='Microbial Diversity',index=False)
	for column in i_df:
		column_width = max(i_df[column].astype(str).map(len).max(), len(column))
		col_idx = i_df.columns.get_loc(column)
		writer.sheets['Microbial Diversity'].set_column(col_idx, col_idx, column_width)
	writer.save()

def no_file(sample_id):
	null_data = {'Error':['Unable to assign taxonomic labels to Input sequences']}
	n_df = pd.DataFrame(null_data)
	create_excel(sample_id,n_df)
	return False

def clear_cache(patient_ids, locations):
	for patient_id in patient_ids:		
		for x in locations:
			try:
				filelist=[f for f in os.listdir(x)]
				for f in filelist:
					if patient_id in f:
						os.remove(os.path.join(x,f))
			except:
				pass

def uploadfiles(s3,sample_id,metadata):
	for k,v in metadata['locs'].items():
		for z in v:
			s3.upload_file(k+'/'+sample_id+z,'webserver-deployment-data','tbpipeline/'+k+'/'+sample_id+z)

def break_columns(adf, species_set):
	all_states=[]
	max_len=0
	for i,r in adf.iterrows():
		a_state={}
		all_words = r['Microbial Diversity'].split(' ')
		for x in all_words:
			a_state[x] = False
			if x.lower() in species_set:
				a_state[x] = True
		all_states.append(a_state)
	adf = adf.drop(['Microbial Diversity'],axis=1)
	max_len=0
	all_texts=[]
	for i,r in adf.iterrows():
		to_insert = all_states[i]
		a_text = []
		p_state = None
		text_to_add=''
		for k,v in to_insert.items():
			c_state = v
			if p_state==None:
				text_to_add = k+' '
				if k==[*to_insert][-1]:
					a_text.append(text_to_add)
			elif p_state==c_state:
				text_to_add +=k+' '
				if k==[*to_insert][-1]:
					a_text.append(text_to_add)
			elif p_state!=c_state:
				a_text.append(text_to_add)
				text_to_add = k+' '
			p_state = c_state
		if len(a_text)> max_len:
			max_len= len(a_text)
		all_texts.append(a_text)
	md_col=[]
	for i in range(max_len):
		md_col.append('Microbial Diversity'+str(i+1))
		adf['Microbial Diversity'+str(i+1)]=''
	adf = adf[md_col+adf.columns.tolist()[:2]]
	
	for i,r in adf.iterrows():
		if list(all_states[i].values())[0]:
			count = 1
		else:
			count = 2
		for x in all_texts[i]:
			adf.at[i,'Microbial Diversity'+str(count)]=x
			count+=1
	return adf

def get_excel_sheet(sample_id, species_set):
		df = pd.read_csv('results/'+sample_id+'_Taxaids.txt', header = None, sep = '	')
		df = df.groupby(df[2]).size().reset_index(name='count')
		df = df.rename(columns={2: 'Microbial Diversity', 'count': 'Read Density'})
		df['Read Density(%)'] = ((df['Read Density'] / df['Read Density'].sum()) * 100).round(2).astype(str) + ' %'
		df = df.sort_values('Read Density',ascending = False).head(10).reset_index(drop=True)
		call_status = df['Microbial Diversity'].str.contains("mycobacterium tuberculosis", case=False).any()
		df = break_columns(df, species_set)
		writer = pd.ExcelWriter(os.path.join('excel_results',str(sample_id+'.xlsx')), engine='xlsxwriter')
		df.to_excel(writer, sheet_name='Microbial Diversity',index=False)
		for column in df:
			column_width = max(df[column].astype(str).map(len).max(), len(column))
			col_idx = df.columns.get_loc(column)
			writer.sheets['Microbial Diversity'].set_column(col_idx, col_idx, column_width)
		writer.save()
		return call_status

def get_max_time(s3, sample_id, completetime, q):
	ref={0:'nanopore/'+sample_id,1:'single/'+sample_id,2:'paired/'+sample_id+'/'+sample_id+'.json'}
	result_f = {'dst':'.xlsx','ntm':'.xlsx','qc':'.html','mcd':'.xlsx'}
	uploaded_file = s3.list_objects_v2(Bucket='webserver-deployment', Prefix='tbpipeline/'+ref[q])
	all_time=[]
	for k,v in result_f.items():
		a_file = s3.list_objects_v2(Bucket='webserver-deployment', Prefix='tbpipeline/results/'+k+'/'+sample_id+v)
		if 'Contents' in a_file:
			all_time.append(abs(int((a_file['Contents'][0]['LastModified']-uploaded_file['Contents'][0]['LastModified']).total_seconds())))
	if len(all_time)>1 and max(all_time) > completetime:
		completetime = max(all_time)
	return completetime

def all_file_confirmation(s3, sample_id, q, start_time, call_status, status_, links):
	flag = "ERR"
	if status_:
		# if call_status:
		# 	flag = "Y"
		# else:
		# 	flag = "N"
		flag = "COM"
		botresponse = requests.get('http://'+links[1]+':80?files='+sample_id+'&type=mcd')
		time.sleep(10)
	conn = sqlq.connect(user="docker",password="Docker@123456789",host="10.10.40.132",database="aarogya")
	cursor = conn.cursor()
	completetime = int(time.time()-start_time)
	completetime = get_max_time(s3, sample_id, completetime, q)
	if len(sample_id)==36:
		query = "UPDATE files SET MCDFlag= %s, completetime = %s WHERE fileID= %s"
	else:
		query = "UPDATE files SET MCDFlag= %s, completetime = %s WHERE filePairKey= %s"
	values = (flag, completetime, sample_id)
	cursor.execute(query, values)
	conn.commit()
	cursor.close()

def download_and_rename(sample_id, s3):
	file_loc = 'tbpipeline/nanopore/'
	conn = sqlq.connect(user="docker", password="Docker@123456789", host="10.10.40.132", database="aarogya")
	cursor = conn.cursor()
	query = "SELECT fileName FROM files WHERE fileID = %s OR filePairKey = %s"
	values = (sample_id, sample_id)
	cursor.execute(query, values)
	res = (cursor.fetchall())[0]
	conn.commit()
	cursor.close()
	if res[0].find(".gz")==-1:
		s3.download_file('webserver-deployment',file_loc+sample_id,'sorted_bam/'+sample_id+'.fastq')
		subprocess.call(['pigz','sorted_bam/'+sample_id+'.fastq'])
	else:
		s3.download_file('webserver-deployment',file_loc+sample_id,'sorted_bam/'+sample_id+'.fastq.gz')

def generate_file(sample_id, q, metadata, links, species_set):
	time.sleep(random.randint(5, links[2]))
	eqn = len(os.listdir('queue'))
	try:
		if eqn<2:
			try:
				if sample_id+'.txt' in os.listdir('all_queue'):
					subprocess.call(['mv','all_queue/'+sample_id+'.txt','queue/'+sample_id+'.txt'])
				else:
					with open('queue/'+sample_id+'.txt', 'w') as fp:
						pass
				status_=True
				start_time = time.time()
				s3 = boto3.client("s3",region_name='ap-south-1')
				if q==0:
					download_and_rename(sample_id, s3)
					prefix = 'n'
				else:
					fastq = s3.download_file('webserver-deployment-data','tbpipeline/bam/'+sample_id+'.sorted.bam','sorted_bam/'+sample_id+'.sorted.bam')
					if len(sample_id)!=36:
						prefix = ''
					else:
						prefix = 's'
				bio_status1 = subprocess.call(['sh', prefix+'demo.sh',sample_id])
				if bio_status1 == 0 and sample_id+'_Taxaids.txt' in os.listdir('results'):
					s3.upload_file('results/'+sample_id+'_Taxaids.txt','webserver-deployment-data','tbpipeline/'+'taxaids/'+sample_id+'.txt')
					call_status = get_excel_sheet(sample_id, species_set)
				else:
					call_status='ERR'
					status_ = no_file(sample_id)
			except:
				call_status='ERR'
				status_ = no_file(sample_id)
			s3.upload_file('excel_results/'+sample_id+'.xlsx','webserver-deployment','tbpipeline/results/mcd/'+sample_id+'.xlsx')
			all_file_confirmation(s3, sample_id, q, start_time, call_status, status_, links)
			clear_cache([sample_id+'.',sample_id+'_'],['.','results','sorted_bam','excel_results','queue'])
		else:
			with open('all_queue/'+sample_id+'.txt', 'w') as fp:
				pass
			print('Saved in all_queue folder.')
			generate_file(sample_id, q, metadata, links, species_set)
	except:
		clear_cache([sample_id+'.',sample_id+'_'],['.','results','sorted_bam','excel_results','queue'])

with open('genes/species_file.txt') as file:
	lines = file.readlines()
	lines = [line.rstrip() for line in lines]
species_set = set(lines)

locs = {'taxaids':['_Taxaids.txt']}
metadata = {'locs':locs,'dev':['172.31.33.7','65.1.248.114',10,'dev'],
'pro':['internal-Aarogya-Internal-ALB-785557005.ap-south-1.elb.amazonaws.com','10.10.20.150',30,'pro']}

app=Flask(__name__)
@app.route('/', methods=['GET'])
def welcome():
	sample_id=str(request.args.get('files'))
	q=int(request.args.get('q'))
	env=str(request.args.get('env'))
	try:
		p=multiprocessing.Process(target=generate_file, args=(sample_id, q, metadata, metadata[env], species_set, ))
		p.start()
		return 'Files of '+sample_id+' saved in the folder.'
	except:
		return 'Unable to download files of '+sample_id+'.'
@app.route('/health', methods=['GET'])
def health_check():
	return Response("healthy",200)

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8005)
