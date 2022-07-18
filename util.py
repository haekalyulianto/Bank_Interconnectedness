from pyvis.network import Network
import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.simplefilter(action='ignore')

def rupiah(num):
  return "Rp{:,}".format(num).replace(',','.') + ',00' 
  
def inputo(df1, df2):
  #df1 = Data Penempatan Dana
  #df2 = LBU Rasio Alat Likuid 
  df1['Total Penempatan'] = np.NaN
  df1['Total Kewajiban'] = np.NaN
  df1['Penempatan/AL'] = np.NaN
  df1['Kewajiban/AL'] = np.NaN
  for i in range (len(df1)):
    for j in range(len(df2)):
      if(df1['BankPelapor'].iloc[i] == df2['Sandi Bank'].iloc[j]):
        df1['Total Penempatan'].iloc[i] = df2['Penem Bank Lain IDR'].iloc[j]
        df1['Total Kewajiban'].iloc[i] = df2['Kewajiban Bank Lain IDR'].iloc[j]
        df1['Penempatan/AL'].iloc[i] = df1['Total Penempatan'].iloc[i]/df2['Total AL'].iloc[j]
        df1['Kewajiban/AL'].iloc[i] = df1['Total Kewajiban'].iloc[i]/df2['Total AL'].iloc[j]
  return df1

def calculate_penempatan_total (df1):
  #df1 = Data Penempatan Dana
  #df2 = LBU Rasio Alat Likuid 
  df1['Persentase Penempatan'] = np.NaN
  for i in range (len(df1)):
      df1['Persentase Penempatan'].iloc[i] =  df1['Jumlah Bulan Laporan'].iloc[i]/df1['Total Penempatan'].iloc[i] 
  return df1

def calculate_penempatan_total (df1):
  #df1 = Data Penempatan Dana
  #df2 = LBU Rasio Alat Likuid 
  df1['Persentase Penempatan'] = np.NaN
  for i in range (len(df1)):
      df1['Persentase Penempatan'].iloc[i] =  df1['Jumlah Bulan Laporan'].iloc[i]/df1['Total Penempatan'].iloc[i] 
  return df1

def view_all(df):
  graph = nx.Graph()
  for i in range (len(df)):
    if  not int(df['BankTujuan'].iloc[i]) in graph:
      graph.add_node(int(df['BankTujuan'].iloc[i]), label=str(df['BankTujuan'].iloc[i]))
    if not int(df['BankPelapor'].iloc[i]) in graph:
      graph.add_node(int(df['BankPelapor'].iloc[i]), label=str(df['BankPelapor'].iloc[i]))
    if not (int(df['BankPelapor'].iloc[i]) in graph.neighbors(int(df['BankTujuan'].iloc[i]))):
      graph.add_edge(int(df['BankPelapor'].iloc[i]), int(df['BankTujuan'].iloc[i]), weight = int(df['Jumlah Bulan Laporan'].iloc[i]))
  
  nt = Network('500px', '500px', directed=True, bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
  nt.from_nx(graph)
  nt.save_graph('/tmp/graph_all.html')

def view_data_from_bank_level(df, inputbankasal, n, df2):
  def get_label(df3, kode_bank):
    df3 = df3[['Sandi Bank', 'Nama Bank']]
    return df3.set_index('Sandi Bank').T.to_dict('index')['Nama Bank'][kode_bank]

  def node_input(df0, df2, graph, x, list_df3):
    if (x < n):
      list_df3.append(df0)
      for i in range (len(df0)):
        if not int(df0['BankTujuan'].iloc[i]) in graph:
          graph.add_node(int(df0['BankTujuan'].iloc[i]), label=str(df0['BankTujuan'].iloc[i]), title=get_label(df2, int(df0['BankTujuan'].iloc[i])))
        if not int(df0['BankPelapor'].iloc[i]) in graph:
          graph.add_node(int(df0['BankPelapor'].iloc[i]), label=str(df0['BankPelapor'].iloc[i]), title=get_label(df2, int(df0['BankPelapor'].iloc[i])))
        
        graph.add_edge(int(df0['BankPelapor'].iloc[i]), int(df0['BankTujuan'].iloc[i]), value=int(df0['Jumlah Bulan Laporan'].iloc[i]), title=rupiah(df0['Jumlah Bulan Laporan'].iloc[i]))
        df1 = df[(df['BankPelapor'] == df0['BankTujuan'].iloc[i])]
        graph, df3 = node_input(df1, df2, graph, x+1, list_df3)

    return graph, list_df3

  inputbankasal = df2.loc[df2['Nama Bank'] == inputbankasal]['Sandi Bank'].iloc[0]

  df1 = df[(df['BankPelapor'] == inputbankasal)]
  list_df3 = []

  graph = nx.Graph()
  graph.add_node(int(inputbankasal), label=str(inputbankasal), title=get_label(df2, inputbankasal), color = 'red')
  
  graph, list_df3 = node_input(df1, df2, graph, 0, list_df3)

  df3 = list_df3[0]
  for i in range(1, len(list_df3)):
    df3 = pd.concat([df3, list_df3[i]], sort=False)

  nt = Network('500px', '500px', directed=True, bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
  nt.from_nx(graph)
  nt.save_graph('/tmp/graph_bank_level.html')

  return df3.reset_index(drop=True)

def simple_cycles(G, cycle_num, cycle_len):
  count_cycles = 0
  flag_cycle = 0

  def _unblock(thisnode, blocked, B):
    stack = {thisnode}
    while stack:
      node = stack.pop()
      if node in blocked:
        blocked.remove(node)
        stack.update(B[node])
        B[node].clear()

  subG = type(G)(G.edges())
  sccs = [scc for scc in nx.strongly_connected_components(subG) if len(scc) > 1]

  for v in subG:
    if subG.has_edge(v, v):
      yield [v]
      subG.remove_edge(v, v)

  while sccs:
    scc = sccs.pop()
    sccG = subG.subgraph(scc)

    startnode = scc.pop()

    path = [startnode]
    blocked = set()  
    closed = set()  
    blocked.add(startnode)
    B = defaultdict(set) 
    stack = [(startnode, list(sccG[startnode]))]  
    while stack:
      thisnode, nbrs = stack[-1]
      if nbrs:
        nextnode = nbrs.pop()
        if nextnode == startnode:
          if (len(path) <= cycle_len):
            yield path[:]
            closed.update(path)
            count_cycles += 1
            if (count_cycles == cycle_num):
              flag_cycle = 1
              break

        elif nextnode not in blocked:
          path.append(nextnode)
          stack.append((nextnode, list(sccG[nextnode])))
          closed.discard(nextnode)
          blocked.add(nextnode)

          continue
      if (flag_cycle == 1):
        break

      if not nbrs:  
        if thisnode in closed:
          _unblock(thisnode, blocked, B)
        else:
          for nbr in sccG[thisnode]:
            if thisnode not in B[nbr]:
              B[nbr].add(thisnode)
            
        stack.pop()
  
        path.pop()

    H = subG.subgraph(scc)  
    sccs.extend(scc for scc in nx.strongly_connected_components(H) if len(scc) > 1)
    if (count_cycles >= cycle_num):
      break

def filter_bank(df, min_persentase_penempatan = None, max_persentase_penempatan = None, min_penempatan_per_al = None, 
                max_penempatan_per_al = None, min_kewajiban_per_al = None, max_kewajiban_per_al = None):
  
  if (min_persentase_penempatan is None):
    min_persentase_penempatan = df['Persentase Penempatan'].min()
  if (max_persentase_penempatan is None):
    max_persentase_penempatan = df['Persentase Penempatan'].max()
  if (min_penempatan_per_al is None):
    min_penempatan_per_al = df['Penempatan/AL'].min()
  if (max_penempatan_per_al is None):
    max_penempatan_per_al = df['Penempatan/AL'].max()
  if (min_kewajiban_per_al is None):
    min_kewajiban_per_al = df['Kewajiban/AL'].min()
  if (max_kewajiban_per_al is None):
    max_kewajiban_per_al = df['Kewajiban/AL'].max()

  df1 = df.copy()
  df1 = df1[df1['Persentase Penempatan'] >= min_persentase_penempatan]
  df1 = df1[df1['Persentase Penempatan'] <= max_persentase_penempatan]
  df1 = df1[df1['Penempatan/AL'] >= min_penempatan_per_al]
  df1 = df1[df1['Penempatan/AL'] <= max_penempatan_per_al]
  df1 = df1[df1['Kewajiban/AL'] >= min_kewajiban_per_al]
  df1 = df1[df1['Kewajiban/AL'] <= max_kewajiban_per_al]

  return df1

def view_data_cycle_all(df, cycle_num, cycle_len, df2):
  def find_bank(df1, kode_bank):
    posisi = 0
    for i in range(len(df1)):
      if (df1['BankPelapor'].iloc[i] == kode_bank):
        posisi = i
        break
    
    return posisi

  def get_label(df2, kode_bank):
    df2 = df2[['Sandi Bank', 'Nama Bank']]
    return df2.set_index('Sandi Bank').T.to_dict('index')['Nama Bank'][kode_bank]

  graph = nx.DiGraph()
  for i in range (len(df)):
    if not int(df['BankTujuan'].iloc[i]) in graph:
      graph.add_node(int(df['BankTujuan'].iloc[i]), label=str(df['BankTujuan'].iloc[i]))
    if not int(df['BankPelapor'].iloc[i]) in graph:
      graph.add_node(int(df['BankPelapor'].iloc[i]), label=str(df['BankPelapor'].iloc[i]))
    if not (int(df['BankPelapor'].iloc[i]) in graph.neighbors(int(df['BankTujuan'].iloc[i]))):
      graph.add_edge(int(df['BankPelapor'].iloc[i]), int(df['BankTujuan'].iloc[i]), weight=int(df['Jumlah Bulan Laporan'].iloc[i]))

  list_cycle = list(simple_cycles(graph, cycle_num, cycle_len))

  list_kodebank = []
  list_namabank = []
  list_countbank = []
  
  # Count Bank
  for i in range(len(list_cycle)):
    for j in range(len(list_cycle[i])):
      if (list_cycle[i][j] not in list_kodebank):
        list_kodebank.append(list_cycle[i][j])
        list_namabank.append(get_label(df2, int(list_cycle[i][j])))
        list_countbank.append(1)
      else:
        idx = list_kodebank.index(list_cycle[i][j])
        list_countbank[idx] += 1

  cycle_graph = nx.MultiDiGraph()

  # Add to Node
  for i in range (len(list_cycle)):
    cycle_graph.add_node(str(list_cycle[i][0]) + '.' + str(i), group=str(i), label=str(list_cycle[i][0]), title=get_label(df2, int(list_cycle[i][0])))
    for j in range (1, len(list_cycle[i])):
      cycle_graph.add_node(str(list_cycle[i][j]) + '.' + str(i), group=str(i), label=str(list_cycle[i][j]), title=get_label(df2, int(list_cycle[i][j])))
      if not (cycle_graph.has_edge(str(list_cycle[i][j-1]) + '.' + str(i), str(list_cycle[i][j]) + '.' + str(i))):
        pos_bank = find_bank(df, list_cycle[i][j-1])
        cycle_graph.add_edge(str(list_cycle[i][j-1]) + '.' + str(i), str(list_cycle[i][j]) + '.' + str(i), value = int(df['Jumlah Bulan Laporan'].iloc[pos_bank]), title=rupiah(df['Jumlah Bulan Laporan'].iloc[pos_bank]))
    if not (cycle_graph.has_edge(str(list_cycle[i][len(list_cycle[i])-1]) + '.' + str(i), str(list_cycle[i][0]) + '.' + str(i))):
      pos_bank = find_bank(df, list_cycle[i][len(list_cycle[i])-1])
      cycle_graph.add_edge(str(list_cycle[i][len(list_cycle[i])-1]) + '.' + str(i), str(list_cycle[i][0]) + '.' + str(i), value = int(df['Jumlah Bulan Laporan'].iloc[pos_bank]), title=rupiah(df['Jumlah Bulan Laporan'].iloc[pos_bank]))

  nt = Network('500px', '500px', directed=True, bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
  nt.from_nx(cycle_graph)
  nt.save_graph('tmp/graph_cycle.html')

  df3 = pd.DataFrame({'Kode Bank': list_kodebank, 'Nama Bank': list_namabank, 'Jumlah Kemunculan': list_countbank})
  df3['Persentase Kemunculan'] = (df3['Jumlah Kemunculan'] / cycle_num)
  df3 = df3.sort_values(by = ['Jumlah Kemunculan'], ascending=False)
  df3 = df3.reset_index(drop=True)

  return df3

# Generate all placement to certain bank
def generate_placement_to_bank(df, inputbankasal, df2):
  inputbankasal = df2.loc[df2['Nama Bank'] == inputbankasal]['Sandi Bank'].iloc[0]

  df1 = df[(df['BankTujuan'] == inputbankasal)]
  df3 = pd.DataFrame(columns=list(df1.columns))
  
  i = 0
  while(i < len(df1)):
    if (not df1['BankPelapor'].iloc[i] in list(df3['BankTujuan'])):
      df1 = df1.append(df[df['BankTujuan'] == df1['BankPelapor'].iloc[i]])
    
    flag = 0
    if (df1['BankPelapor'].iloc[i] in list(df3['BankPelapor'])):
      dftemp = df3[df3['BankPelapor'] == df1['BankPelapor'].iloc[i]]
      if (df1['BankTujuan'].iloc[i] in list(dftemp['BankTujuan'])):
        flag = 1

    if (flag == 0):
      df3 = df3.append(df1.iloc[i])

    i += 1

  df3 = df3[['BankTujuan', 'BankPelapor', 'Jumlah Bulan Laporan',
       'Persentase Penempatan', 'Total Penempatan', 'Total Kewajiban',
       'Penempatan/AL', 'Kewajiban/AL']]
  
  return df3.reset_index(drop=True)

# Generate all placement from certain bank
def generate_placement_from_bank(df, inputbankasal, df2):
  inputbankasal = df2.loc[df2['Nama Bank'] == inputbankasal]['Sandi Bank'].iloc[0]

  df1 = df[(df['BankPelapor'] == inputbankasal)]
  df3 = pd.DataFrame(columns=list(df1.columns))
  
  i = 0
  while(i < len(df1)):
    if (not df1['BankTujuan'].iloc[i] in list(df3['BankPelapor'])):
      df1 = df1.append(df[df['BankPelapor'] == df1['BankTujuan'].iloc[i]])
    
    flag = 0
    if (df1['BankPelapor'].iloc[i] in list(df3['BankPelapor'])):
      dftemp = df3[df3['BankPelapor'] == df1['BankPelapor'].iloc[i]]
      if (df1['BankTujuan'].iloc[i] in list(dftemp['BankTujuan'])):
        flag = 1

    if (flag == 0):
      df3 = df3.append(df1.iloc[i])

    i += 1

  return df3.reset_index(drop=True)
