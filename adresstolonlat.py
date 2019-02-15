import pandas as pd
import requests
import numpy as np

ak='05adbb65534de230a677f2d0386fa093'

def address_name(address):
    url="http://restapi.amap.com/v3/geocode/geo?key=%s&address=%s"%(ak,address)
    data=requests.get(url)
    contest=data.json()
    contest=contest['geocodes'][0]['location']
    return contest.split(',')

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.deg2rad, [lon1, lat1, lon2, lat2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    m = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    dis = 2 * np.arcsin(np.sqrt(m)) * 6378.137 * 1000
    return dis

def run():
    df_g = pd.read_excel('基础工参.xlsx')
    df_d = pd.read_excel('需转换地址.xlsx')

    df_d['经度'] = df_d.apply(lambda x: address_name(x['投诉现场地址'])[0], axis=1)
    df_d['纬度'] = df_d.apply(lambda x: address_name(x['投诉现场地址'])[1], axis=1)

    df_d['经度'] = df_d['经度'].astype(np.float64)
    df_d['纬度'] = df_d['纬度'].astype(np.float64)

    df_g['经度'] = df_g['经度'].astype(np.float64)
    df_g['纬度'] = df_g['纬度'].astype(np.float64)
    
    len_g = df_g.shape[0]
    print ('请输入您要查询的距离范围(单位米):')
    num = input('Number=')
    print(f'您需要查询的距离为{num}米，正在查询中，请等待...')
    float_num = float(num)

    df_ls = []
    for i, address in enumerate(df_d['投诉现场地址']):
        name = np.repeat(address, len_g)
        lat1 = np.repeat(df_d['纬度'].iloc[i], len_g)
        lon1 = np.repeat(df_d['经度'].iloc[i], len_g)

        xlsdata = pd.DataFrame({
            '投诉现场地址': name, 
            '纬度': lat1,
            '经度': lon1,
            '最近基站': df_g['基站名称'],
            '最近纬度': df_g['纬度'],
            '最近经度': df_g['经度'],
            })     

        xlsdata['最近距离(M)'] = haversine(lon1, lat1, df_g['经度'].values, df_g['纬度'].values)
        xlsdata = xlsdata.loc[xlsdata['最近距离(M)'] != 0]
        xlsdata = xlsdata.sort_values(by='最近距离(M)', ascending=True)
        xlsdata = xlsdata.loc[xlsdata['最近距离(M)'] < float_num]
        df_ls.append(xlsdata)

    df = pd.concat(df_ls, axis=0)
    df['最近距离(M)'] = df['最近距离(M)'].values
    df.to_csv('地址转换查询结果.csv',encoding='gbk',index=None,columns=['投诉现场地址','经度','纬度','最近基站','最近经度','最近纬度','最近距离(M)'])
    print("查询结果已输出为结果.csv")
    
if __name__ == '__main__':
    print("正在读取数据，请等待...")
    run()
