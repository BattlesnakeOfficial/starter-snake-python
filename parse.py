import json
import numpy as np

if __name__ == '__main__':
    with open('data.json') as json_file:
        json = json.load(json_file)
    
    height = json["board"]["height"]
    width = json["board"]["width"]
    foods = json["board"]["food"]
    
    snakes = json["board"]["snakes"]
    
    print('Snake heads:')
    for snake in snakes:
        print(snake["head"])
    
    
    me = json["you"]
    
    my_health = json["you"]["health"]
    
    my_body = json["you"]["body"]
    
    my_head = json["you"]["head"]
    
    my_length = json["you"]["length"]
    
    print('----- Other stuff ------')
    num_redirected = 2
    actions = np.random.rand(4) # Walmart Q-values
    print(actions)
    action = int(np.argmax(actions))
    print(action)
    sort = np.argsort(actions)
    print(sort)
    action = sort[-num_redirected]
    print(action)
    
    print('For loop testing\n')
    for i in range(0, 5):
        print(i)
        for j in range(10,15):
            if j == 11: continue
            print(j)
            
