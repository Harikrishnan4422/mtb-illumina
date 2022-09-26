import pandas as pd
import os

def get_excel_sheet(sample_id):
		# df = pd.read_csv('results/'+sample_id+'_Taxaids.txt', header = None, sep = '	')
		df = pd.read_csv(sample_id+'.txt', header = None, sep = '	')
		df = df.groupby(df[2]).size().reset_index(name='count')
		df = df.rename(columns={2: 'Microbial Density', 'count': 'Read Density'})
		df['Read Density(%)'] = ((df['Read Density'] / df['Read Density'].sum()) * 100).round(2).astype(str) + ' %'
		df = df.sort_values('Read Density',ascending = False).head(10)
		writer = pd.ExcelWriter(os.path.join('excel_results',str(sample_id+'.xlsx')), engine='xlsxwriter')
		df.to_excel(writer, sheet_name='Microbial Density',index=False)
		for column in df:
			column_width = max(df[column].astype(str).map(len).max(), len(column))
			col_idx = df.columns.get_loc(column)
			writer.sheets['Microbial Density'].set_column(col_idx, col_idx, column_width)
		writer.save()
		call_status = df['Microbial Density'].str.contains("mycobacterium tuberculosis", case=False).any()
		return call_status
get_excel_sheet('PRD8jgxxqMpfezgoo7zc188')