from itertools import chain

from gali_shelli import GaliShelli


class ShelliFormatter:
    def __init__(self):
        self._proposals_name_encoding: dict[str, int] = dict()
        self._proposals_name_decoding: dict[int, str] = dict()
        self._acceptors_name_encoding: dict[str, int] = dict()
        self._acceptors_name_decoding: dict[int, str] = dict()
        self._acceptors_mux_encoding: dict[int, list[int]] = dict()
        self._acceptors_mux_decoding: dict[int, int] = dict()

    def fit(self, students_priorities: dict[str, list[str]], directions_priorities: dict[str, list[str]],
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
        proposals_name_decoding: dict[int, str] = {name_code: name for name, name_code in
                                                   proposals_name_encoding.items()}
        acceptors_name_encoding: dict[str, int] = {x: i for i, x in enumerate(directions_priorities)}
        acceptors_name_decoding: dict[int, str] = {name_code: name for name, name_code in
                                                   acceptors_name_encoding.items()}

        # multiplying acceptors encoding
        total_mux_count = 0
        acceptors_mux_encoding: dict[int, list[int]] = dict()
        for acc_coded_name, max_count in acceptors_max_accept_count.items():
            acc_coded_name = acceptors_name_encoding[acc_coded_name]
            acceptors_mux_encoding[acc_coded_name] = list(range(total_mux_count, total_mux_count + max_count))
            total_mux_count += max_count
        acceptors_mux_decoding: dict[int, int] = dict()
        for acc_coded_name, acc_mux_codes in acceptors_mux_encoding.items():
            for acc_mux_code in acc_mux_codes:
                acceptors_mux_decoding[acc_mux_code] = acc_coded_name

        self._proposals_name_encoding = proposals_name_encoding
        self._proposals_name_decoding = proposals_name_decoding
        self._acceptors_name_encoding = acceptors_name_encoding
        self._acceptors_name_decoding = acceptors_name_decoding
        self._acceptors_mux_encoding = acceptors_mux_encoding
        self._acceptors_mux_decoding = acceptors_mux_decoding

        return self.encode(students_priorities, directions_priorities, directions_max_accept_count)
        # format_data(students_priorities, directions_priorities, directions_max_accept_count)

    def encode(self, students_priorities: dict[str, list[str]], directions_priorities: dict[str, list[str]],
               directions_max_accept_count: dict[str, int] = None) -> tuple[list[list[int]], list[list[int]]]:
        proposals_priorities: dict[str, list[str]] = students_priorities
        acceptors_priorities: dict[str, list[str]] = directions_priorities

        proposals_name_encoding = self._proposals_name_encoding
        acceptors_name_encoding = self._acceptors_name_encoding
        acceptors_mux_encoding = self._acceptors_mux_encoding

        # apply encoding
        X_priorities = [
            [acceptors_name_encoding[prop_priorities] for prop_priorities in proposals_priorities[prop_name]]
            for prop_name in proposals_priorities]
        Y_priorities = [[proposals_name_encoding[acc_priorities] for acc_priorities in acceptors_priorities[acc_name]]
                        for acc_name in acceptors_priorities]
        Y_places = {acceptors_name_encoding[acc_name]: max_count for acc_name, max_count in
                    directions_max_accept_count.items()}
        # apply mux encoding to Y_priorities
        X_priorities_mux = [list(chain(*[acceptors_mux_encoding[acc_id] for acc_id in prop_priorities]))
                            for prop_priorities in X_priorities]
        Y_priorities_mux = list(chain(*[[acc_priorities for _ in range(Y_places[acc_id])]
                                        for acc_id, acc_priorities in enumerate(Y_priorities)]))

        # it's finale
        return X_priorities_mux, Y_priorities_mux

    def decode(self, X_priorities: list[list[int]], Y_priorities: list[list[int]]) \
            -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        proposals_name_decoding = self._proposals_name_decoding
        acceptors_name_decoding = self._acceptors_name_decoding
        acceptors_mux_decoding = self._acceptors_mux_decoding

        X_priorities_back_mux = [[acceptors_mux_decoding[acc_mux_code] for acc_mux_code in prop_properties
                                  if acc_mux_code >= 0]
                                 for prop_properties in X_priorities]
        # concat same numbers
        X_priorities_back_mux_concat = [list(dict.fromkeys(prop_priorities)) for prop_priorities in
                                        X_priorities_back_mux]
        # concat same lines
        Y_priorities_back_concat = []
        demux_acc_num_was = 0
        for acc_num in range(len(Y_priorities)):
            acc_priorities = Y_priorities[acc_num]
            demux_acc_num = acceptors_mux_decoding[acc_num]
            if acc_num < 1:
                demux_acc_num_was = demux_acc_num
                Y_priorities_back_concat += [acc_priorities]
                continue
            if demux_acc_num_was != demux_acc_num:
                demux_acc_num_was = demux_acc_num
                Y_priorities_back_concat += [acc_priorities]
                continue
            demux_acc_num_was = demux_acc_num

        # for acc_num in range(len(Y_priorities)):
        #     acc_priorities = Y_priorities[acc_num]
        #     if acc_num < 1:
        #         Y_priorities_back_concat += [acc_priorities]
        #         continue
        #     acc_priorities_was = Y_priorities[acc_num - 1]
        #     if len(acc_priorities) != len(acc_priorities_was):
        #         Y_priorities_back_concat += [acc_priorities]
        #         continue
        #     for pr_num in range(len(acc_priorities)):
        #         if acc_priorities[pr_num] != acc_priorities_was[pr_num]:
        #             Y_priorities_back_concat += [acc_priorities]
        #             break

        X_priorities_back_names_decode = [
            [acceptors_name_decoding[acc_name_coded] for acc_name_coded in prop_properties]
            for prop_properties in X_priorities_back_mux_concat]
        Y_priorities_back_names_decode = [
            [proposals_name_decoding[prop_name_coded] for prop_name_coded in acc_properties if prop_name_coded >= 0]
            for acc_properties in Y_priorities_back_concat]
        X_priorities_back_dict = {proposals_name_decoding[prop_name_pos]: prop_properties
                                  for prop_name_pos, prop_properties in enumerate(X_priorities_back_names_decode)}
        Y_priorities_back_dict = {acceptors_name_decoding[acc_num]: acc_properties
                                  for acc_num, acc_properties in enumerate(Y_priorities_back_names_decode)}
        return X_priorities_back_dict, Y_priorities_back_dict

    def decode_result(self, X_answers: list[int], Y_answers: list[int]) \
            -> tuple[dict[str, str], dict[str, list[str]]]:
        proposals_name_decoding = self._proposals_name_decoding
        acceptors_name_decoding = self._acceptors_name_decoding
        acceptors_mux_decoding = self._acceptors_mux_decoding

        # X demux
        X_answers_name_coded = [acceptors_mux_decoding[acc_mux_code] if acc_mux_code >= 0 else -1
                                for acc_mux_code in X_answers]
        # X decode name
        X_answers_decoded = {proposals_name_decoding[prop_name_coded]: acceptors_name_decoding[acc_name_coded]
                             if acc_name_coded >= 0 else '-1'
                             for prop_name_coded, acc_name_coded in enumerate(X_answers_name_coded)}

        # concat based on mux
        Y_answers_concat = dict()
        demux_acc_num_was = -1
        demux_acc_num = demux_acc_num_was
        Y_answers_coded_grouped_by_mux: dict[int, list[int]] = dict()
        for acc_num_mux in range(len(Y_answers)):
            prop_name_coded = Y_answers[acc_num_mux]
            acc_name_coded = acceptors_mux_decoding[acc_num_mux]
            if acc_name_coded not in Y_answers_coded_grouped_by_mux:
                Y_answers_coded_grouped_by_mux[acc_name_coded] = []
            Y_answers_coded_grouped_by_mux[acc_name_coded].append(prop_name_coded)

        Y_answers_decoded: dict[str, list[str]] = dict()
        for acc_name_coded, props in Y_answers_coded_grouped_by_mux.items():
            acc_name = acceptors_name_decoding[acc_name_coded]
            Y_answers_decoded[acc_name] = [proposals_name_decoding[prop_name_coded] if prop_name_coded >= 0 else '-1'
                                           for prop_name_coded in props]

        return X_answers_decoded, Y_answers_decoded


# noinspection DuplicatedCode


def main():
    g = GaliShelli()
    X = {'0': ['1', '2'],
         '1': ['2', '1'],
         '55': ['2'],
         '3': ['1']}

    Y = {'1': ['0', '55', '1'],
         '2': ['3', '1', '55', '0']}
    Y_places = {'1': 1, '2': 3}
    f = ShelliFormatter()
    X1, Y1 = f.fit(X, Y, Y_places)
    pairsX, pairsY = g.fit(X1, Y1)
    resX, resY = f.decode([pairsX], [pairsY])
    pass


if __name__ == '__main__':
    main()
