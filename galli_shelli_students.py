import itertools

from gali_shelli import GaliShelli


class GaliShelliStudents:
    def __init__(self):
        self._g = GaliShelli()

    def fit(self, students_priorities: dict[str, list[str]], directions_priorities: dict[str, list[str]],
            directions_max_accept_count: dict[str, int] = None) -> list[int]:
        """
        Misha operates big poop factories ᕦ(ò_óˇ)ᕤ
        """
        day = 1
        proposals_priorities: dict[str, list[str]] = students_priorities
        acceptors_priorities: dict[str, list[str]] = directions_priorities
        acceptors_max_accept_count: dict[str, int] = directions_max_accept_count
        proposals_count = len(proposals_priorities)
        acceptors_count = len(acceptors_priorities)
        # verify
        for prop_priorities in proposals_priorities.values():
            for suggested_acceptor_name in prop_priorities:
                if suggested_acceptor_name not in directions_priorities:
                    raise ValueError(f"Направление \"{suggested_acceptor_name}\" не найдено "
                                     f"в списке directions_priorities")
        for acc_priorities in acceptors_priorities.values():
            for suggested_proposal_name in acc_priorities:
                if suggested_proposal_name not in students_priorities:
                    raise ValueError(f"Студент \"{suggested_proposal_name}\" не найден "
                                     f"в списке students_priorities")
        # encode names to numbers
        # proposals_name_encoding = {x: i for i, x in enumerate(students_priorities.keys())}
        # acceptors_name_encoding = {x: i for i, x in enumerate(directions_priorities.keys())}

        # proposals
        # acceptors
        proposals_pairs: dict[str, str] = dict()
        proposals_pairs_was = proposals_pairs.copy()
        acceptors_pairs: dict[str, str] = dict()

        # prepare steps
        proposals_priorities_stops_steps: dict[str, list[int]] = dict()
        for prop_name, prop_priorities in proposals_priorities.items():
            max_step = 0
            stop_steps = [0] * len(prop_priorities)
            for prop_priority_num, prop_priority_name in enumerate(prop_priorities):
                acc_max_accept_count = acceptors_max_accept_count.get(prop_priority_name, 1)
                stop_step = max_step + acc_max_accept_count
                stop_steps[prop_priority_num] = stop_step
                max_step = stop_step
            proposals_priorities_stops_steps[prop_name] = stop_steps

        # main loop
        proposals_loop_elements = proposals_priorities.copy()  # for optimization loop
        for priority_num in itertools.count(0):
            day = priority_num + 1
            if len(proposals_pairs) >= proposals_count:
                print("Все предложения приняты. Распределение завершено")
                break
            print(f"День {day}")

            for selected_proposal in proposals_loop_elements.copy():
                if selected_proposal in proposals_pairs:
                    continue
                selected_proposal_priorities = proposals_priorities[selected_proposal]
                selected_proposal_stops_steps = proposals_priorities_stops_steps[selected_proposal]
                max_stop_step = max(selected_proposal_stops_steps)
                if priority_num >= max_stop_step:
                    proposals_loop_elements.pop(selected_proposal)
                    continue

                selected_proposal_priority_used = 0
                for stop_step_num, stop_step in enumerate(selected_proposal_stops_steps):
                    if priority_num >= stop_step:
                        break
                    selected_proposal_priority_used = stop_step_num
                selected_acceptor = selected_proposal_priorities[selected_proposal_priority_used]
                selected_acceptor_priorities = acceptors_priorities[selected_acceptor]

                # Если принимающий не имеет интереса к подающему
                if selected_proposal not in selected_acceptor_priorities:
                    continue

                paired_proposal = acceptors_pairs.get(selected_acceptor, None)
                if paired_proposal is not None:
                    paired_proposal_priority = acceptors_priorities[selected_acceptor].index(paired_proposal)
                    selected_proposal_priority = selected_acceptor_priorities.index(selected_proposal)
                    if selected_proposal_priority < paired_proposal_priority:  # less is better
                        proposals_pairs.pop(paired_proposal)
                        proposals_pairs[selected_proposal] = selected_acceptor
                        acceptors_pairs[selected_acceptor] = selected_proposal
                else:
                    proposals_pairs[selected_proposal] = selected_acceptor
                    acceptors_pairs[selected_acceptor] = selected_proposal
            print(proposals_pairs, acceptors_pairs)
            # pairs_stable = True
            # for x_num in range(x_count):
            #     if x_pairs[x_num] != x_pairs_was[x_num]:
            #         pairs_stable = False
            #         break
            # if pairs_stable:
            #     break
            proposals_pairs_was = proposals_pairs.copy()
        return proposals_pairs
