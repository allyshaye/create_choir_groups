import csv
import sys


def save_as_bool(str):
  val = False
  if str == 'TRUE':
    val = True

  return val


def save_pref(pref_str):
  if 'Saturday 8am' in pref_str:
    return 'sat_8'
  elif 'Saturday 11am' in pref_str:
    return 'sat_11'
  elif 'Sunday 7am' in pref_str:
    return 'sun_7'
  elif 'Sunday 10am' in pref_str:
    return 'sun_10'


def save_group_num(group_str):
  if group_str == 'Group 1':
    return 1
  elif group_str == 'Group 2':
    return 2
  elif group_str == 'Group 3':
    return 3


def save_survey_results(results_csv):
  choirmembers = {}
  with open(results_csv) as f:
    reader = csv.DictReader(f, fieldnames=("timestamp", "name", "group", "voice", "pref_1", "pref_2", "pref_3", "cws"))
    for row in reader:
      if row['timestamp'] != 'Timestamp':
        person = {}
        person['name'] = row['name']
        person['group'] = save_group_num(row['group'])
        person['voice'] = row['voice']
        person['pref_1'] = save_pref(row['pref_1'])
        person['pref_2'] = save_pref(row['pref_2'])
        person['pref_3'] = save_pref(row['pref_3'])
        person['cws_officer'] = save_as_bool(row['cws'])
        person['fully_assigned'] = False
        choirmembers[person['name']] = person

  return choirmembers


def get_voice_totals(choir_list, voice):
  count = 0
  for name, info in choir_list.items():
    if info['voice'] == voice:
      count += 1

  return count


def get_voice_totals_per_service(choir_list):
  totals = {
    'Soprano': get_voice_totals(choir_list, 'Soprano') / 2,
    'Alto': get_voice_totals(choir_list, 'Alto') / 2,
    'Tenor': get_voice_totals(choir_list, 'Tenor') / 2,
    'Bass': get_voice_totals(choir_list, 'Bass') / 2
  }

  return totals


def establish_base_groups(choir_list):
  groupings = {
    'sat_8': {'Soprano': [], 'Alto': [], 'Tenor': [], 'Bass': []},
    'sat_11': {'Soprano': [], 'Alto': [], 'Tenor': [], 'Bass': []},
    'sun_7': {'Soprano': [], 'Alto': [], 'Tenor': [], 'Bass': []},
    'sun_10': {'Soprano': [], 'Alto': [], 'Tenor': [], 'Bass': []}
  }

  for name, info in choir_list.items():
    group = info['group']
    voice = info['voice']
    if group == 1:
      groupings['sat_8'][voice].append(info['name'])
    elif group == 2:
      groupings['sun_7'][voice].append(info['name'])
    elif group == 3:
      groupings['sun_10'][voice].append(info['name'])

  return groupings


def get_pref_by_voice(pref_level, service, voice, choir_list):
  choir_by_voice = []
  for name, info in choir_list.items():
    if info['fully_assigned'] == False:
      if info[pref_level] == service:
        if info['voice'] == voice:
          choir_by_voice.append(info['name'])

  return choir_by_voice


def add_and_mark_assigned(list_to_add, list_to_update_assigned, name, worship_service):
  list_to_update_assigned[name]['fully_assigned'] = True
  list_to_add.append(name)
  list_to_update_assigned[name]['additional_service'] = worship_service


def handle_more_volunteers_than_spots(num_needed, list_to_add, avail_choir_list, master_choir_list, worship_service):
  for i in range(0,num_needed):
    add_and_mark_assigned(list_to_add,
      master_choir_list, 
      avail_choir_list[i],
      worship_service)


def handle_less_equal_volunteers_to_spots(volunteer_list, list_to_add, master_choir_list, worship_service):
  for volunteer in volunteer_list:
    add_and_mark_assigned(list_to_add,
      master_choir_list,
      volunteer,
      worship_service)


def handle_sat_11_group(avail_choir_list, num_needed, list_to_add, master_choir_list, worship_service):
  if len(avail_choir_list) <= num_needed:
    handle_less_equal_volunteers_to_spots(avail_choir_list,
      list_to_add,
      master_choir_list,
      worship_service)
  else:
      handle_more_volunteers_than_spots(num_needed,
        list_to_add,
        avail_choir_list,
        master_choir_list,
        worship_service)


def handle_not_sat11_group(cws_officers, non_cws_officers, num_needed, list_to_add, master_choir_list, required_voice_num, worship_service):

  current_voice_num = len(list_to_add)

  if len(cws_officers) <= num_needed:
    handle_less_equal_volunteers_to_spots(cws_officers,
      list_to_add,
      master_choir_list,
      worship_service)

    updated_num_needed = required_voice_num - current_voice_num

    if updated_num_needed > 0:
      handle_more_volunteers_than_spots(updated_num_needed,
        list_to_add,
        non_cws_officers,
        master_choir_list,
        worship_service)
  else:
    handle_more_volunteers_than_spots(num_needed,
      list_to_add,
      cws_officers,
      master_choir_list,
      worship_service)


def handle_leftovers(leftover_list, groupings, choir_list):
  for choirmember in leftover_list:
    indiv_info = choir_list[choirmember]
    voice = indiv_info['voice']
    groupings_voice_totals = {
      'sat_8': len(groupings['sat_8'][voice]),
      'sat_11': len(groupings['sat_8'][voice]),
      'sun_7': len(groupings['sat_8'][voice]),
      'sun_10': len(groupings['sat_8'][voice]),
    }

    largest_group = max(groupings_voice_totals, 
      key=groupings_voice_totals.get)

    for pref in ['pref_1', 'pref_2', 'pref_3']:
      if indiv_info[pref] != largest_group:
        add_and_mark_assigned(
          groupings[indiv_info[pref]][voice],
          choir_list,
          choirmember,
          indiv_info[pref])
        break
    


def create_groups(choir_list):
  groupings = establish_base_groups(choir_list)

  TOTALS_PER_SERVICE = get_voice_totals_per_service(choir_list)
  
  preferences = ['pref_1', 'pref_2', 'pref_3']

  for pref in preferences:
    for worship_service, choirmembers in groupings.items():
      for voice, individuals in choirmembers.items():
        if len(individuals) < TOTALS_PER_SERVICE[voice]:
          num_needed = TOTALS_PER_SERVICE[voice] - len(individuals)

          available_volunteers = get_pref_by_voice(pref, 
            worship_service, 
            voice, 
            choir_list)

          cws_officers = filter(lambda name: 
            choir_list[name]['cws_officer'] == True, 
            available_volunteers)

          non_cws_officers = filter(lambda name: 
            choir_list[name]['cws_officer'] == False, 
            available_volunteers)

          if len(available_volunteers) <= num_needed:
            handle_less_equal_volunteers_to_spots(available_volunteers,
              choirmembers[voice],
              choir_list,
              worship_service)
          else: 
            if worship_service != 'sat_11':
              handle_not_sat11_group(cws_officers, 
                non_cws_officers, 
                num_needed, 
                choirmembers[voice], 
                choir_list, TOTALS_PER_SERVICE[voice],
                worship_service)
            else: 
              handle_sat_11_group(non_cws_officers, 
                num_needed, 
                choirmembers[voice], 
                choir_list,
                worship_service)

  leftovers = [k for (k,v) in choir_list.items() if v['fully_assigned'] == False]

  handle_leftovers(leftovers, groupings, choir_list)

  return groupings


def write_val_to_csv(list):
  if list:
    return list.pop()
  else:
    return ''


def convert_bool_to_str(bool_variable):
  if bool_variable == True:
    return 'Yes'
  else:
    return 'No'


def write_groups_to_csv(groupings):
  for service, groups_by_voice in groupings.items():
    with open(service + '.csv', 'wb') as f:
      fieldnames=['Soprano', 'Alto', 'Tenor', 'Bass']
      writer = csv.DictWriter(f, fieldnames=fieldnames)

      writer.writeheader()
      for i in range(0,len(groups_by_voice['Soprano'])):
        writer.writerow({
          'Soprano': write_val_to_csv(groups_by_voice['Soprano']),
          'Alto': write_val_to_csv(groups_by_voice['Alto']),
          'Tenor': write_val_to_csv(groups_by_voice['Tenor']),
          'Bass': write_val_to_csv(groups_by_voice['Bass'])
          })



def write_choir_to_csv(choir_list):
  with open('choir_list_yetg_2018.csv', 'wb') as f:
    fieldnames = ['Name', 'Group', 'Voice', 'CWS Officer?', '1st Pick', '2nd Pick', '3rd Pick', 'Fully Assigned?', 'Additional Service']
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    for name, info in choir_list.items():
      writer.writerow({
        'Name': info['name'],
        'Group': info['group'],
        'Voice': info['voice'],
        'CWS Officer?': convert_bool_to_str(info['cws_officer']),
        '1st Pick': info['pref_1'],
        '2nd Pick': info['pref_2'],
        '3rd Pick': info['pref_3'],
        'Fully Assigned?': convert_bool_to_str(info['fully_assigned']),
        'Additional Service': info['additional_service']
        })






def main():
  survey_csv_file = sys.argv[-1]
  choirmembers = save_survey_results(survey_csv_file)
  groups = create_groups(choirmembers)
  write_groups_to_csv(groups)
  write_choir_to_csv(choirmembers)



if __name__ == '__main__':
  main()
