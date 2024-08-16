import os
import pathlib

import numpy as np
import pandas as pd

import gali_shelli
import shelli_formatter

lists_folder = 'lists'


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
    print(res_table)
    #
    pass


    pass


if __name__ == '__main__':
    main()
