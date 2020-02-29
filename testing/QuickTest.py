GetFieldsList = set([ \
'annualreturn2009', \
'annualreturn2010', \
'annualreturn2011', \
'annualreturn2012', \
'annualreturn2013', \
'annualreturn2014', \
'annualreturn2015', \
'annualreturn2016', \
'annualreturn2017', \
'annualreturn2018', \
'averageannualreturnyear01', \
'averageannualreturnyear01', \
'averageannualreturnyear05', \
'averageannualreturnyear05', \
'averageannualreturnyear10', \
'averageannualreturnyear10', \
'distributionandservice12b1feesoverassets', \
'expensesoverassets', \
'managementfeesoverassets', \
'otherexpensesoverassets', \
'portfolioturnoverrate', \
'shareholderfeeother', \
 '9z'])

s = 'annualReturn2009'

if s.lower() in GetFieldsList:
    print("yes")