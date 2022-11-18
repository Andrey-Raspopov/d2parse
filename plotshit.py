import matplotlib.pyplot as plt
import json
x = open('1','r').read().split('\n')
entities_x = {}
entities_y = {}
for item in x[:-1]:
    item = json.loads(item)
    if item['entity'] not in entities_x:
        entities_x[item['entity']] = [item['x']]
        entities_y[item['entity']] = [item['y']]
    else:
        entities_x[item['entity']].append(item['x'])
        entities_y[item['entity']].append(item['y'])

img = plt.imread("dota_map.jpg")
fig, ax = plt.subplots()
ax.imshow(img)
fig, ax = plt.subplots()
x = range(300)
ax.imshow(img, extent=[-16000,0 , 0, 16000])
for item in entities_x.keys():
    ax.scatter(entities_x[item],entities_y[item])
plt.show()