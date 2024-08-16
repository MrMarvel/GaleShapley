import os
import pathlib

import numpy as np
import pandas as pd

import gali_shelli
import shelli_formatter

lists_folder = 'lists'


def get_direction_passed(df, direction_name, max_passes):
    df_direction = df[df['Направление'] == direction_name]
    count_direction = int(df_direction.count().max())
    if count_direction <= max_passes:
        return count_direction
    df_sorted = df_direction.sort_values(by=['Итоговый балл', 'Баллы за экзамены', 'Средняя оценка'], ascending=False)
    df_sorted.reset_index(drop=True, inplace=True)
    return df_sorted.head(max_passes)


def solve_direction(df_system, target_directions, max_passes_list):
    if len(df_system['Направление'].value_counts()) != len(max_passes_list):
        raise ValueError(f"Длина max_passes_list не совпадает с количеством направлений df_system")
    if (len(df_system[df_system['Направление'].isin(target_directions)]['Направление'].value_counts()) !=
            len(target_directions)):
        raise ValueError(f"Некоторые target_directions не содержатся в df_system")
    df_sorted = df_system.sort_values(by=['Итоговый балл', 'Баллы за экзамены', 'Средняя оценка'], ascending=False,
                                      ignore_index=True)
    target_direction = target_directions[0]
    df_direction = df_sorted[df_sorted['Направление'] == target_direction]
    count_direction = int(df_direction.count().max())
    if count_direction <= max_passes_list[0]:
        return count_direction

    target_result_df = df_sorted
    return target_result_df


def main():
    files = []
    # .csv files in lists folder
    if not os.path.exists(lists_folder):
        os.makedirs(lists_folder)

    for dir_item in pathlib.Path(lists_folder).iterdir():
        if not os.path.isfile(dir_item):
            continue
        file = dir_item
        if not file.suffix == '.csv':
            continue
        files.append(str(file))
    # pass
    directions_count = len(files)
    types = {'СНИЛС': str, 'Приоритет': np.uint8, 'Итоговый балл': np.uint16,
             'Средняя оценка': np.float32, 'Дополнительный балл': np.uint16}
    defaults = {'Дополнительный балл': 0, 'Средняя оценка': 0}
    directions_names = [''] * len(files)
    directions_max = [0] * len(files)
    df_merged = pd.DataFrame()
    for direction_num in range(directions_count):
        file = files[direction_num]
        file = pathlib.Path(file)
        filename = file.name
        prefix = filename.removesuffix(file.suffix)
        directions_names[direction_num] = prefix[:prefix.find('max')].removesuffix('-')
        info_items = prefix[filename.find('max'):].split('-')
        free_max = 0
        if len(info_items) > 1:
            free_max = int(info_items[1])
        directions_max[direction_num] = free_max
        df = pd.read_csv(file, usecols=list(types.keys()))
        # reorder
        df = df[types.keys()]
        # приведение типов
        df.astype(types, errors='ignore', copy=False)
        for col in types.keys():
            col_type = types[col]
            if np.issubdtype(col_type, np.floating):
                df[col] = df[col].str.replace(',', '.')
        for col in defaults.keys():
            df[col] = df[col].fillna(defaults[col])
        df.astype(types, errors='raise', copy=False)
        pass
        df['Направление'] = directions_names[direction_num]
        df.insert(df.columns.to_list().index('Итоговый балл') + 1, 'Баллы за экзамены',
                  df['Итоговый балл'] - df['Дополнительный балл'])
        df_merged = pd.concat([df_merged, df], ignore_index=True)
        # df.to_csv(file, index=False)
    df_sorted = df_merged.sort_values(by=['Итоговый балл', 'Баллы за экзамены', 'Средняя оценка'], ascending=False)
    priority = 1
    max_priority = int(df_merged['Приоритет'].max())
    df_phase = df_sorted.copy()
    # reindex
    df_phase.reset_index(drop=True, inplace=True)
    target_directions = ['priem-09-04-01']
    solve_direction(df_system=df_sorted, target_directions=target_directions, max_passes_list=directions_max)

    people_sorted = []
    people_max_priority = df_sorted.groupby('СНИЛС')['Приоритет'].max()
    people_count_priority = df_sorted.groupby('СНИЛС')['Приоритет'].count()
    people_lacks_count = people_max_priority - people_count_priority
    people_lacks_any_directions = people_lacks_count[people_lacks_count != 0]
    people_lacks_directions_dict = dict()
    people_lacks_directions_dict_back = dict()

    # new method
    df_priorities_sorted = df_sorted.sort_values(by=['СНИЛС', 'Приоритет'], ascending=True)
    people_priorities: dict[str, list[str]] = dict()
    unique_people = df_sorted['СНИЛС'].unique().tolist()
    people_priorities = {man_id: df_priorities_sorted[df_priorities_sorted['СНИЛС'] == man_id]['Направление'].to_list()
                         for man_id in unique_people}
    directions_priorities: dict[str, list[str]] = dict()
    directions_priorities = {direction_name: df_sorted[df_sorted['Направление']
                                                       == direction_name]['СНИЛС'].to_list()
                             for direction_name in directions_names}
    directions_accept_count: dict[str, int] = dict()
    directions_accept_count = {direction_name: directions_max[direction_num]
                               for direction_num, direction_name in enumerate(directions_names)}
    f = shelli_formatter.ShelliFormatter()
    X, Y = f.fit(people_priorities, directions_priorities, directions_accept_count)
    g = gali_shelli.GaliShelli()
    answers = g.fit(X, Y)
    X_res, Y_res = f.decode_result(*answers)
    dir_tables = []
    for dir_name in directions_names:
        dir_table = df_sorted[(df_sorted['Направление'] == dir_name) & (df_sorted['СНИЛС'].isin(Y_res[dir_name]))]
        dir_table = dir_table.sort_values(by=['Итоговый балл', 'Баллы за экзамены', 'Средняя оценка'], ascending=False,
                                          ignore_index=True)
        dir_tables.append(dir_table)
    res_table = pd.concat(dir_tables, ignore_index=True)
    #
    pass
    for man_id in people_lacks_any_directions.index:
        man_priorities = df_sorted[df_sorted['СНИЛС'] == man_id]['Приоритет'].to_list()
        man_max_priority = people_max_priority[man_id]
        lacks_priorities = set(range(1, man_max_priority + 1)) - set(man_priorities)
        people_lacks_directions_dict[man_id] = lacks_priorities
        for priority in lacks_priorities:
            if priority not in people_lacks_directions_dict_back:
                people_lacks_directions_dict_back[priority] = []
            people_lacks_directions_dict_back[priority].append(man_id)
        pass
    for priority in range(1, max_priority + 1):
        count_priority = int(df_merged[df_merged['Приоритет'] == priority].count().max())
        if count_priority <= 0:
            continue
        all_people = df_phase['СНИЛС'].unique()
        # exclude people with priority from all people
        people_passed_lacks_directions = []
        # Вывод пропущенных
        # if len(people_lacks_directions) > 0:
        #     print(f'Пропущены люди с приоритетом {priority}:\n{people_lacks_directions}')
        for direction_num in range(len(files)):
            current_direction_pass = get_direction_passed(df_phase, directions_names[direction_num],
                                                          directions_max[direction_num])
            direction_name = directions_names[direction_num]
            free_max = directions_max[direction_num]
            df_direction = df_phase[df_phase['Направление'] == directions_names[direction_num]]
            count_direction = int(df_direction.count().max())
            if count_direction <= free_max:
                continue
            df_most_priority = df_direction[df_direction['Приоритет'] <= priority]
            count_direction_priority = int(df_most_priority.count().max())
            if count_direction_priority <= free_max:
                continue
            first_elements = df_most_priority.head(free_max)
            # check if there are people not fully checked in people_lacks_directions
            lacked_elements = np.intersect1d(people_lacks_directions_dict_back[priority], first_elements['СНИЛС'])
            if len(lacked_elements) > 0:
                print(f'Удалены люди с приоритетом {priority} из направления {direction_name}:\n{lacked_elements}')
                df_phase = df_phase.drop(df_phase[df_phase['СНИЛС'].isin(lacked_elements)].index)
                continue
            # remove them from others directions with higher priority
            # df_global_first_elements = first_elements[first_elements['СНИЛС'].isin(first_elements['СНИЛС'])]
            # elements_to_remove = df_global_first_elements[df_global_first_elements['Приоритет'] > priority]
            # df_phase = df_phase.drop(elements_to_remove.index)
            # remove people same priority worse
            last_elements = df_most_priority.tail(count_direction_priority - free_max)
            contains_my = last_elements[last_elements['СНИЛС'].str.startswith('172-165')]
            df_phase = df_phase.drop(last_elements.index)
            # remove people with worse score all priorities
            worst_score = int(first_elements['Итоговый балл'].min())
            worst_elements = df_direction[df_direction['Итоговый балл'] < worst_score]
            df_phase = df_phase.drop(worst_elements.index, errors='ignore')

    pass


if __name__ == '__main__':
    main()
