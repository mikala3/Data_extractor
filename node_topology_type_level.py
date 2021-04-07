from prometheus_api_client import PrometheusConnect
import json


prometheus_host = 'http://localhost:9090'
app = 'bookinfo'
prom = PrometheusConnect(url = prometheus_host, disable_ssl=True)

metrics_data = prom.custom_query(query="istio_requests_total")

topology_json = {
                    "components": [],
                    "links": []
                }

service_dict = {}
link_counter = 1
#keep track on which services already extracted
extracted_services = []

for item in metrics_data:
    element_inserted = False
    #service_source = item['metric']['source_canonical_service']
    try:
        component = item['metric']['app']

        #check if component is an istio component
        namespace = item['metric']['source_workload_namespace']
        #service_destination_version = item['metric']['version']

        #this two will be the destination of the link
        #service_destination = item['metric']['destination_canonical_service']
        service_destination = item['metric']['destination_service_name']
        #connection_point = item['metric']['destination_canonical_revision']
        if(namespace != "istio-system"):
            #loop through all data from prometheus, each component is an application
            for _ in range(len(topology_json['components'])):

                if(component in topology_json['components'][_]['component_id']):
                    connection_point_exist = False
                    element_inserted = True
                    for i in range(len(topology_json['components'][_]['connection_point'])):
                        if(component == topology_json['components'][_]['component_id']):
                            if("service_"+service_destination == topology_json['components'][_]['connection_point'][i]['connection_point_id']):
                                connection_point_exist = True
                            #else:
                            #    topology_json['components'][_]['connection_point'].append({'connection_point_id': "service_"+service_destination})


                   # if(not(connection_point_exist)):


                    if(component != service_destination and connection_point_exist == False):
                        link_exist = False
                        for k in range(len(topology_json['links'])):
                            if(topology_json['links'][k]['cp_reference'][0]['component_id_reference'] == component and topology_json['links'][k]['cp_reference'][1]['component_id_reference'] == service_destination):
                                link_exist = True
                            elif(topology_json['links'][k]['cp_reference'][1]['component_id_reference'] == component and topology_json['links'][k]['cp_reference'][0]['component_id_reference'] == service_destination):
                                link_exist = True
                        
                        if(not(link_exist)):
                            #topology_json['components'][_]['connection_point'].append({'connection_point_id': "service_"+service_destination})
                            topology_json['links'].append({
                                                            'link_id': 'link '+str(link_counter),
                                                            'cp_reference': [] 

                            })  
                            topology_json['links'][-1]['cp_reference'].append({'component_id_reference': component,
                                                                'connection_point_id_reference': "service_"+component
                            })
                            topology_json['links'][-1]['cp_reference'].append({'component_id_reference': service_destination,
                                                                'connection_point_id_reference': "service_"+service_destination
                            })
                            link_counter += 1                    


            if(not(element_inserted)):
                topology_json['components'].append({
                                                    'component_id':component,
                                                    'connection_point': []
                })
                topology_json['components'][-1]['connection_point'].append({'connection_point_id': "service_"+component})
            
                if(component != service_destination):
                    #topology_json['components'][-1]['connection_point'].append({'connection_point_id': "service_"+component})
                    topology_json['links'].append({
                                                    'link_id': 'link '+str(link_counter),
                                                    'cp_reference': [] 

                    })   

                    topology_json['links'][-1]['cp_reference'].append({'component_id_reference': component,
                                                        'connection_point_id_reference': "service_"+component
                    })
                    topology_json['links'][-1]['cp_reference'].append({'component_id_reference': service_destination,
                                                        'connection_point_id_reference': "service_"+service_destination
                    })
                    link_counter += 1  

    except:
        pass
        # if(service_source in service_dict):

        #     if(not(service_destination in service_dict[service_source])):
        #         service_dict[service_source].append(service_destination)

        # else:
        #     service_dict[service_source] = [service_destination]

def get_component_element(component_id, topology):
    try:
        for _ in range(len(topology['components'])):
            if component_id == topology['components'][_]['component_id']:
                component_element = topology['components'][_]
                return component_element
    except:
        return []
    return []

def trace_links(component_id, component_element):
    #
    links = False
    for i in range(len(topology_json['links'])):
        if component_id == topology_json['links'][i]['cp_reference'][1]['component_id_reference']:
            links = True
            new_component_id = topology_json['links'][i]['cp_reference'][0]['component_id_reference']
            #print("hej",new_component_id)
            component_element3 = get_component_element(new_component_id, topology_json)
            new_component_element = get_component_element(new_component_id, topology_json)
            if len(topology_json2['components']) == 0:
                topology_json2['components'].append(component_element)
                topology_json2['links'].append(topology_json['links'][i])
                trace_links(new_component_id, new_component_element)
                #print(component_id)
            elif len(get_component_element(new_component_id, topology_json2)) == 0:
                #print("hej",new_component_id)
                #print("hej",component_element3)
                topology_json2['components'].append(component_element3)
                topology_json2['links'].append(topology_json['links'][i])
                trace_links(new_component_id, new_component_element)
                #print(component_id)
            else:
                break
    if links == False:
        return topology_json2['components'].append(component_element)


def check_if_link_exists(link, topology):
    for i in range(len(topology['links'])):
        if link == topology['links'][i]:
            return True
    return False

def trace_links2(component_id, component_element):
    #
    links = False
    for i in range(len(topology_json['links'])):
        if component_id == topology_json['links'][i]['cp_reference'][1]['component_id_reference']:
            links = True
            new_component_id = topology_json['links'][i]['cp_reference'][0]['component_id_reference']
            #print("hej",new_component_id)
            component_element3 = get_component_element(new_component_id, topology_json)
            new_component_element = get_component_element(new_component_id, topology_json)
            if len(topology_json2['components']) == 0:
                extracted_services.append(component_id)
                extracted_services.append(new_component_id)
                topology_json2['components'].append(component_element)
                topology_json2['components'].append(component_element3)
                topology_json2['links'].append(topology_json['links'][i])
                trace_links2(new_component_id, new_component_element)
                #print(component_id)
            elif len(get_component_element(new_component_id, topology_json2)) == 0:
                #print("hej",new_component_id)
                #print("hej",component_element3)
                topology_json2['components'].append(component_element3)
                extracted_services.append(new_component_id)
                if len(get_component_element(component_id, topology_json2)) == 0:
                    topology_json2['components'].append(component_element)
                    extracted_services.append(component_id)
                if not(check_if_link_exists(topology_json['links'][i], topology_json2)):
                    topology_json2['links'].append(topology_json['links'][i])
                trace_links2(new_component_id, new_component_element)
                #print(component_id)
        elif component_id == topology_json['links'][i]['cp_reference'][0]['component_id_reference']:
            links = True
            new_component_id = topology_json['links'][i]['cp_reference'][1]['component_id_reference']
            #print("hej",new_component_id)
            component_element3 = get_component_element(new_component_id, topology_json)
            new_component_element = get_component_element(new_component_id, topology_json)
            if len(topology_json2['components']) == 0:
                extracted_services.append(component_id)
                extracted_services.append(new_component_id)
                topology_json2['components'].append(component_element)
                topology_json2['components'].append(component_element3)
                topology_json2['links'].append(topology_json['links'][i])
                trace_links2(new_component_id, new_component_element)
                #print(component_id)
            elif len(get_component_element(new_component_id, topology_json2)) == 0:
                #print("hej",new_component_id)
                #print("hej",component_element3)
                topology_json2['components'].append(component_element3)
                extracted_services.append(new_component_id)
                if len(get_component_element(component_id, topology_json2)) == 0:
                    topology_json2['components'].append(component_element)
                    extracted_services.append(component_id)
                if not(check_if_link_exists(topology_json['links'][i], topology_json2)):
                    topology_json2['links'].append(topology_json['links'][i])
                trace_links2(new_component_id, new_component_element)
                #print(component_id)
            # else:
            #     break
    if links == False:
        return topology_json2['components'].append(component_element)
print(json.dumps(topology_json, indent=4))
print("--------------------------------------------------------------")

def check_extracted_services(service):
    for s in extracted_services:
        if s == service:
            return True
    return False

##########todo CHECK RESPONSE CODE IN PROMETHEUS, 404 will be a valid link
for _ in range(len(topology_json['components'])):
    component_id = topology_json['components'][_]['component_id']
    component_element = topology_json['components'][_]

    already_extracted = check_extracted_services(component_id)
    if(already_extracted):
        pass
    else:
        topology_json2 = {
                        "components": [],
                        "links": []
                    }

        trace_links2(component_id, component_element)

        f = open("topology_"+str(_)+".txt", "w")
        f.write(json.dumps(topology_json2, indent=4))
        f.close()