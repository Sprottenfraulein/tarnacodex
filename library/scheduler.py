# schedule manager object
from library import counter


class Scheduler(counter.Counter):
    def __init__(self, fps, spr, max_rounds, history_size=6):
        super().__init__(fps, spr, max_rounds)

        self.schedules = {}
        self.history_size = history_size

    def new_schedule(self, sch_label):
        self.schedules[sch_label] = [0, []]

    def task_add(self, sch_label, rounds_delta, task_object, task_function_name, task_attrs):
        rounds_counter = self.rounds + rounds_delta
        if rounds_counter <= self.rounds:
            return

        schedule = self.schedules[sch_label]

        new_task = (rounds_counter, task_object, task_function_name, task_attrs)

        for i in range(0, len(schedule[1]) - 1):
            if schedule[1][i][0] <= rounds_counter < schedule[1][i+1][0]:
                schedule[1].insert(i+1, new_task)
        else:
            schedule[1].append(new_task)

    def tick(self):
        super().tick()

        if self.frame != 0 or self.step != 0:
            return

        for schedule in self.schedules.values():
            if schedule[0] >= len(schedule[1]):
                continue
            pos_task = schedule[1][schedule[0]]
            if pos_task[0] == self.rounds:
                getattr(pos_task[1], pos_task[2])(*pos_task[3])
                schedule[0] += 1

            if schedule[0] == self.history_size:
                del schedule[1][0]
                schedule[0] -= 1
