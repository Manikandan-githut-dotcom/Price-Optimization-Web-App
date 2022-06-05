# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 11:41:53 2022

@author: Manikandan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import pickle

df = pd.read_csv('C:/Users/Manikandan/Downloads/priceOptimize (1).csv')
df.describe()
df.dropna(inplace = True)
df.isna().sum()
df.columns

df.rename(columns = {"GST Value":"GST_Value", "Sales at Cost":"Sales_at_cost", "SALES AT COST": "Margin", "MARGIN%         ":"MARGIN%"},inplace = True)
df.drop(columns = 'UID', inplace = True)

df = df.loc[df['NSU']> 0]
df = df.loc[df['Sales_at_cost']> 0]
df = df.loc[df['MRP']> 0]
df = df.loc[df['SP']> 0]

min_mrp = min(df['MRP'])
max_mrp = max(df['MRP'])

df = df[['NAME', 'ZONE', 'Brand', 'MC', 'Fdate', 'NSU', 'NSV', 'GST_Value', 'Sales_at_cost', 'Margin', 'MARGIN%', 'MRP', 'SP', 'DIS', 'DIS%']]
df['unit_cost'] = df['Sales_at_cost']/df['NSU']
df['unit_gst'] = df['GST_Value']/df['NSU']

product_counts = df['NAME'].value_counts()

prod_dict = {}
unique_products = df['NAME'].unique().tolist()    

for i in unique_products:
    df2 = df.loc[df['NAME'] == i]
    prod_dict[i] = df2
    
df3 = pd.DataFrame(columns = ['NAME', 'ZONE', 'Intercept', 'SP_coeff', 'Unitcost_coeff', 'Unit_cost', 'Unit_gst'])

for k in prod_dict:
    zone_groups = prod_dict[k].groupby('ZONE')
    zones = zone_groups.groups.keys()
    for i in zones:
        zone_values = zone_groups.get_group(i)
        model = smf.ols('NSU ~ SP + unit_cost', data = zone_values).fit()
        model.summary()
        para = model.params
        cost = prod_dict[k].unit_cost.mean()
        gst = prod_dict[k].unit_gst.mean()
        test = {'NAME':k, 'ZONE': i, 'Intercept': para[0], 'SP_coeff': para[1], 'Unitcost_coeff': para[2], 'Unit_cost': cost, 'Unit_gst': gst}
        df3 = df3.append(test, ignore_index = True)
        
product = input('Enter Product: \n')
zone = input('Enter Zone: \n')
mrp = float(input('Enter MRP: \n'))
value = df3.loc[df3['NAME'] == product]

def get_optimal_price(df3):
    S = []

    for i in np.arange(mrp/2, mrp, 0.01):
        S.append(i)

    intercept = value['Intercept'].values[0]
    spcoef = value['SP_coeff'].values[0]
    uccoef = value['Unitcost_coeff'].values[0]
    cost = value['Unit_cost'].values[0]
    gst = value['Unit_gst'].values[0]
    N = []
    Rev = []
    Dis = []
    Disper = []

    for p in S:
        nsu = (intercept) + (spcoef*p) + (uccoef*cost)
        N.append(nsu)
        # Profit function
        rev = nsu*(p - cost - gst)
        Rev.append(rev)
        dis = mrp - p
        disper = dis/mrp *100
        Dis.append(dis)
        Disper.append(disper)
        
    profit = pd.DataFrame({'NSU': N, 'Price': S, 'Revenue': Rev, 'Discount': Dis, 'Discount%': Disper })
    
    plt.plot(profit['Price'], profit['Revenue'])
    plt.xlabel('Selling_Price')
    plt.ylabel('Revenue')
    plt.axhline(y = 0, linestyle = 'dashed')
    plt.show()  

    optimal_price = np.where(profit['Revenue'] == profit['Revenue'].max())[0][0]
    maximum_profit = profit.iloc[[optimal_price]]
    return maximum_profit
    
    
optimized_price = {}
optimized_price[product] = get_optimal_price(df3)
    
# pickle library for dumping data into file

data = pickle.dump(df3,open('data.pkl','wb'))

pickle.dump(model,open('model.pkl','wb'))

Products = df['NAME'].unique()
Products = pd.Series(Products)

pickle.dump(Products,open('Products.pkl','wb'))

Zone = df['ZONE'].unique()
Zone = pd.Series(Zone)

pickle.dump(Zone,open('Zone.pkl','wb'))
