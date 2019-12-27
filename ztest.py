from pathlib import Path

p = Path('C:\Files2020_Dev\ByProject\Open15C_Data\SEC_IndexFiles').glob('*.idx')
xFiles =  [e for e in p]
for y in xFiles:
    print(y)
print('new')

for e in p:
    print(e)