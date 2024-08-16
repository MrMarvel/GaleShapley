class GaliShelli:
    def __init__(self):
        pass

    def fit(self, X_priorities: list[list[int]], Y_priorities: list[[int]]) -> tuple[list[int], list[int]]:
        """
        [XY]_priorities - список приоритетов каждого участника, в каждом приоритете
        позиция соответствует порядку обращения. Позиция нумерация от 0.
        """
        day = 1
        proposals_priorities: list[list[int]] = X_priorities
        acceptors_priorities: list[list[int]] = Y_priorities
        proposals_count = len(proposals_priorities)
        acceptors_count = len(acceptors_priorities)
        # verify
        proposals_priorities_max_num = max([max(x) for x in proposals_priorities])
        if proposals_priorities_max_num >= acceptors_count:
            raise ValueError(f"Превышен максимальный номер приоритета \"{proposals_priorities_max_num}\" "
                             f"(должно быть <={acceptors_count - 1}) для X_priorities")
        acceptors_priorities_max_num = max([max(x) for x in acceptors_priorities])
        if acceptors_priorities_max_num >= proposals_count:
            raise ValueError(f"Превышен максимальный номер приоритета \"{acceptors_priorities_max_num}\" "
                             f"(должно быть <={proposals_count - 1}) для Y_priorities")
        # proposals
        # acceptors
        proposals_pairs = [-1] * proposals_count
        proposals_pairs_was = proposals_pairs.copy()
        acceptors_pairs = [-1] * acceptors_count
        max_priorities_count = max([len(x) for x in proposals_priorities])
        proposals_loop_elements = list(range(proposals_count))  # for optimization loop
        for priority_num in range(max_priorities_count):
            day = priority_num + 1
            if len([x for x in proposals_pairs if x == -1]) < 1:
                print("Все предложения приняты. Распределение завершено")
                break
            print(f"День {day}")

            for selected_proposal in proposals_loop_elements.copy():
                if proposals_pairs[selected_proposal] >= 0:
                    continue
                selected_proposal_priorities = proposals_priorities[selected_proposal]
                if priority_num >= len(selected_proposal_priorities):
                    proposals_loop_elements.remove(selected_proposal)
                    continue

                selected_acceptor = selected_proposal_priorities[priority_num]
                selected_acceptor_priorities = acceptors_priorities[selected_acceptor]

                # Если принимающий не имеет интереса к подающему
                if selected_proposal not in selected_acceptor_priorities:
                    continue

                paired_proposal = acceptors_pairs[selected_acceptor]
                if paired_proposal >= 0:
                    paired_proposal_priority = acceptors_priorities[selected_acceptor].index(paired_proposal)
                    selected_proposal_priority = selected_acceptor_priorities.index(selected_proposal)
                    if selected_proposal_priority < paired_proposal_priority:  # less is better
                        proposals_pairs[paired_proposal] = -1
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
        return proposals_pairs, acceptors_pairs
