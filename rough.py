import pandas as pd
import os, re

with open('genes/species_file.txt') as file:
	lines = file.readlines()
	lines = [line.rstrip() for line in lines]
species_set = set(lines)

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
get_excel_sheet('PRDQT5uFWCiCpA8gpfRUCWE',species_set)