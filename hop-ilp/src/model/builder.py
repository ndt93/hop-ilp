from tree import Node, Tree
from model import Model
from logger import logger
import json


def from_json_file(filepath):
    logger.info('building_model|json_file={}'.format(filepath))
    with open(filepath, 'r') as f:
        model_data = json.load(f)
        
    if model_data:
        return build_model(model_data)
    return Model()
    

def build_model(model_data):
    model = Model()
    model.variables = model_data['variables']
    model.horizon = model_data['horizon']
    model.actions = model_data['actions']
    model.max_concurrency = model_data['maxConcurrency']
    model.transition_trees = {v: dict_to_tree(t)
                              for (v, t) in model_data['transitionTrees'].items()}
    model.reward_tree = dict_to_tree(model_data['rewardTree'])
    return model
    

def dict_to_tree(tree_dict):
    if tree_dict is None:
        return None
    
    t = Tree()
    if 'node' in tree_dict:
        node_dict = tree_dict['node']
        node = Node(name=node_dict.get('name', ''), value=node_dict.get('value', None))
        if node.name == 'branches' and isinstance(node.value, list):
            node.value = [dict_to_tree(branch) for branch in node.value]
        t.node = node
            
    if 'left' in tree_dict:
        t.left = dict_to_tree(tree_dict['left'])
    if 'right' in tree_dict:
        t.right = dict_to_tree(tree_dict['right'])
        
    return t
