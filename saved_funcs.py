from itertools import chain


def format_data(students_priorities: dict[str, list[str]], directions_priorities: dict[str, list[str]],
                directions_max_accept_count: dict[str, int] = None) -> tuple[list[list[int]], list[list[int]]]:
    proposals_priorities: dict[str, list[str]] = students_priorities
    acceptors_priorities: dict[str, list[str]] = directions_priorities
    acceptors_max_accept_count: dict[str, int] = directions_max_accept_count
    proposals_count = len(proposals_priorities)
    acceptors_count = len(acceptors_priorities)
    # verify
    for prop_priorities in proposals_priorities.values():
        for suggested_acceptor_name in prop_priorities:
            if suggested_acceptor_name not in acceptors_priorities:
                raise ValueError(f"Направление \"{suggested_acceptor_name}\" не найдено "
                                 f"в списке directions_priorities")
    for acc_priorities in acceptors_priorities.values():
        for suggested_proposal_name in acc_priorities:
            if suggested_proposal_name not in proposals_priorities:
                raise ValueError(f"Студент \"{suggested_proposal_name}\" не найден "
                                 f"в списке students_priorities")
    # encode names to numbers

    proposals_name_encoding: dict[str, int] = {x: i for i, x in enumerate(proposals_priorities)}
    proposals_name_decoding: dict[int, str] = {name_code: name for name, name_code in proposals_name_encoding.items()}
    acceptors_name_encoding: dict[str, int] = {x: i for i, x in enumerate(directions_priorities)}
    acceptors_name_decoding: dict[int, str] = {name_code: name for name, name_code in acceptors_name_encoding.items()}

    # apply encoding
    X_priorities = [[acceptors_name_encoding[prop_priorities] for prop_priorities in proposals_priorities[prop_name]]
                    for prop_name in proposals_priorities]
    Y_priorities = [[proposals_name_encoding[acc_priorities] for acc_priorities in acceptors_priorities[acc_name]]
                    for acc_name in acceptors_priorities]
    Y_places = {acceptors_name_encoding[acc_name]: max_count for acc_name, max_count in
                directions_max_accept_count.items()}
    # multiplying acceptors encoding
    total_mux_count = 0
    acceptors_mux_encoding: dict[int, list[int]] = dict()
    for acc_name, max_count in Y_places.items():
        acceptors_mux_encoding[acc_name] = list(range(total_mux_count, total_mux_count + max_count))
        total_mux_count += max_count
    acceptors_mux_decoding: dict[int, int] = dict()
    for acc_name, acc_mux_codes in acceptors_mux_encoding.items():
        for acc_mux_code in acc_mux_codes:
            acceptors_mux_decoding[acc_mux_code] = acc_name
    # apply mux encoding to Y_priorities
    X_priorities_mux = [list(chain(*[acceptors_mux_encoding[acc_id] for acc_id in prop_priorities]))
                        for prop_priorities in X_priorities]
    Y_priorities_mux = list(chain(*[[acc_priorities for _ in range(Y_places[acc_id])]
                                    for acc_id, acc_priorities in enumerate(Y_priorities)]))
    # it's finale
    # back process to test
    X_priorities_back_mux = [[acceptors_mux_decoding[acc_mux_code] for acc_mux_code in prop_properties]
                             for prop_properties in X_priorities_mux]
    # concat same numbers
    X_priorities_back_mux_concat = [list(dict.fromkeys(prop_priorities)) for prop_priorities in X_priorities_back_mux]
    X_priorities_back_names_decode = [[acceptors_name_decoding[acc_name_coded] for acc_name_coded in prop_properties]
                                      for prop_properties in X_priorities_back_mux_concat]
    X_priorities_back_dict = {proposals_name_decoding[prop_name_pos]: prop_properties
                              for prop_name_pos, prop_properties in enumerate(X_priorities_back_names_decode)}

    return X_priorities_mux, Y_priorities_mux
