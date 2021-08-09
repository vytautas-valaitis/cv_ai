import json

with open('full.json') as f:
  data = list(json.load(f).items())
#print(json.dumps(data, indent=1))
data = data[0][1]

print('text,skill')
for d in range(len(data)):
  for j in range(len(data[d]['jobs'])):
    dsk = data[d]['jobs'][j]['skillsFromCV'].replace(',', '').strip()
    pos = data[d]['jobs'][j]['skillsFromExcel']
    if(pos is not None):
      spos = pos.split(',')
      for i in range(len(spos)):
        if(len(spos[i].strip().lower()) > 0):
            if spos[i].strip().lower() in { 'marketing', 'sales', 'project management', 'leading', 'account management', 'analytics', 'business development', 'accounting', 'communication management', 'social media management'}:
              print(dsk, end='')
              print(',', end='')
              print(spos[i].strip().lower())

