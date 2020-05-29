import json
import numpy as np

if __name__ == '__main__':
    with open('data.json') as json_file:
        json = json.load(json_file)
    
    height = json["board"]["height"]
    width = json["board"]["width"]
    foods = json["board"]["food"]
    
    snakes = json["board"]["snakes"]
    me = json["you"]
    my_health = json["you"]["health"]
    
    my_body = json["you"]["body"]
    print('BODY: ', my_body)
    print(len(my_body))
    x, y = my_body[1]["x"], my_body[1]["y"]
    print(x, y)
    
    
    my_head = json["you"]["head"]
    
    x, y = my_head["x"], my_head["y"]
    
    my_length = json["you"]["length"]
    
    print('-----------')
    num_redirected = 2
    actions = np.random.rand(4) # Walmart Q-values
    print(actions)
    action = int(np.argmax(actions))
    print(action)
    sort = np.argsort(actions)
    print(sort)
    action = sort[-num_redirected]
    print(action)
