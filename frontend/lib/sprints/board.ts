import type { CreateTaskInput, SprintTask, SprintTaskStatus } from "./types";

export function moveTaskToStatus(
  tasks: SprintTask[],
  taskId: string,
  nextStatus: SprintTaskStatus,
) {
  const taskIndex = tasks.findIndex((task) => task.id === taskId);
  if (taskIndex < 0) {
    return tasks;
  }

  const targetTask = tasks[taskIndex];
  if (targetTask.status === nextStatus) {
    return tasks;
  }

  const withoutTask = tasks.filter((task) => task.id !== taskId);
  const movedTask: SprintTask = { ...targetTask, status: nextStatus };

  const lastTargetIndex = withoutTask.reduce((lastIndex, task, index) => {
    if (task.status === nextStatus) {
      return index;
    }
    return lastIndex;
  }, -1);

  if (lastTargetIndex === -1) {
    return [...withoutTask, movedTask];
  }

  return [
    ...withoutTask.slice(0, lastTargetIndex + 1),
    movedTask,
    ...withoutTask.slice(lastTargetIndex + 1),
  ];
}

export function createTaskFromInput(input: CreateTaskInput): SprintTask {
  const generatedId = `ENG-${Math.floor(500 + Math.random() * 400)}`;

  return {
    id: generatedId,
    title: input.title,
    priority: input.priority,
    status: input.status,
    dueDate: input.dueDate,
    storyPoints: input.storyPoints,
    tags: input.tags.length ? input.tags : ["General"],
    assigneeIds: input.assigneeIds,
  };
}

