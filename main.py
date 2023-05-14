from lxml import etree, objectify
import datetime
import json
import os

def subparse_generator(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()

    generator = dict()
    definitions_list = list()
    tests = dict()
    objects = dict()
    states = dict()
    variables = dict()

    for child in root.getchildren():
        if child.tag.endswith('generator'):
            for param in child.getchildren():
                param_name = param.tag.split('}')[-1]
                generator[param_name] = param.text
        elif child.tag.endswith('definitions'):
            for definition in child.getchildren():
                definition_dict = dict()

                definition_dict.update(dict(definition.attrib))

                if (definition_dict.get('version')):
                    definition_dict.update(version=int(definition.attrib.get('version')))

                for params in definition.getchildren():
                    if params.tag.endswith('metadata'):
                        metadata_dict = {
                            'affected': [],
                            'reference': []
                        }

                        for param in params.getchildren():
                            param_name = param.tag.split('}')[-1]
                            if param_name == 'affected':
                                for platform in param.getchildren():
                                    metadata_dict['affected'].append(platform.text)
                            elif param_name == 'reference':
                                metadata_dict['reference'].append(dict(param.attrib))
                            else:
                                metadata_dict[param_name] = param.text

                        definition_dict.update(metadata=metadata_dict)
                    elif params.tag.endswith('criteria'):
                        criteria_dict = dict()
                        if params.attrib:
                            criteria_dict.update(dict(params.attrib))

                        for param in params.getchildren():
                            if param.tag.endswith('criteria'):
                                
                                tmp_criteria_dict = dict()
                                tmp_criteria_dict.update(dict(param.attrib))
                                for deep_param in param.getchildren():
                                    if deep_param.tag.endswith('criteria'):
                                        if deep_param.attrib.get('operator'):
                                            tmp_criteria_dict['operator'] = deep_param.attrib.get('operator')
                                        for deepest_param in deep_param.getchildren():
                                            param_name = deepest_param.tag.split('}')[-1]
                                            
                                            if not tmp_criteria_dict.get(param_name):
                                                tmp_criteria_dict[param_name] = list()
                                            tmp_criteria_dict[param_name].append(dict(deepest_param.attrib))
                                    else:
                                        param_name = deep_param.tag.split('}')[-1]
                                        
                                        if not tmp_criteria_dict.get(param_name):
                                            tmp_criteria_dict[param_name] = list()
                                        tmp_criteria_dict[param_name].append(dict(deep_param.attrib))
                                        
                                    
                                if not criteria_dict.get('criterias'):
                                    criteria_dict['criterias'] = list()
                                criteria_dict['criterias'].append(tmp_criteria_dict)
                            else: 
                                param_name = param.tag.split('}')[-1]
                                if not criteria_dict.get(param_name):
                                    criteria_dict[param_name] = list()
                                criteria_dict[param_name].append(dict(param.attrib))

                        definition_dict.update(criteria=criteria_dict)

                definitions_list.append(definition_dict)
        elif child.tag.endswith('tests'):

            for test in child.getchildren():
                test_dict = dict()
                param_name = test.tag.split('}')[-1]
                if not tests.get(param_name):
                    tests[param_name] = list()

                test_dict.update(dict(test.attrib))
                for param in test:
                    tmp_param_name = param.tag.split('}')[-1]
                    if not test_dict.get(tmp_param_name):
                        test_dict[tmp_param_name] = list()

                    test_dict[tmp_param_name].append(dict(param.attrib))
                    
                tests[param_name].append(test_dict)
        elif child.tag.endswith('objects'):
            for obj in child.getchildren():
                obj_dict = dict()
                param_name = obj.tag.split('}')[-1]
                if not objects.get(param_name):
                    objects[param_name] = list()

                obj_dict.update(dict(obj.attrib))

                if (obj_dict.get('version')):
                    obj_dict.update(version=int(obj.attrib.get('version')))

                for param in obj:
                    tmp_param_name = param.tag.split('}')[-1]

                    if not tmp_param_name == 'path':
                        obj_dict[tmp_param_name] = param.text
                    else:
                        obj_dict[tmp_param_name] = dict(param.attrib)
                    
                objects[param_name].append(obj_dict)
        elif child.tag.endswith('states'):
            for state in child.getchildren():
                state_dict = dict()
                param_name = state.tag.split('}')[-1]
                if not states.get(param_name):
                    states[param_name] = list()
                
                state_dict.update(dict(state.attrib))

                if (state_dict.get('version')):
                    state_dict.update(version=int(state.attrib.get('version')))

                for param in state:
                    tmp_param_name = param.tag.split('}')[-1]
                    if param.attrib:
                        state_dict.update(dict(param.attrib))

                    state_dict.update(value=param.text)
                
                states[param_name].append(state_dict)
        elif child.tag.endswith('variables'):
            for var in child.getchildren():
                var_dict = dict()
                param_name = var.tag.split('}')[-1]
                if not variables.get(param_name):
                    variables[param_name] = list()

                var_dict.update(dict(var.attrib))

                if (var_dict.get('version')):
                    var_dict.update(version=int(var.attrib.get('version')))

                    for concat in var.getchildren():
                        for param in concat:
                            tmp_param_name = param.tag.split('}')[-1]
                            if param.attrib:
                                var_dict[tmp_param_name] = dict(param.attrib)
                            else:
                                var_dict[tmp_param_name] = param.text
                    variables[param_name].append(var_dict)
    
    return ('generator', generator), ('definitions', definitions_list), ('tests', tests), ('objects', objects), ('states', states), ('variables', variables)


def parse_xml(xml_file):    
    oval_def_dict = dict()
    for part in subparse_generator(xml_file):
        if part:
            oval_def_dict[part[0]] = part[1]
    
    json_path = os.sep.join([os.getcwd(), 'json', f'{xml_file[5:-4]}.json'])
    with open(json_path, 'w') as outfile:
        json.dump(oval_def_dict, outfile, indent=4)
    

if __name__ == '__main__':
    parse_xml('oval\oval_com.altx-soft.win_def_81925.xml')

