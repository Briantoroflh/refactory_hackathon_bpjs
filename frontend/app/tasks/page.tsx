import { TasksPage } from "@/components/tasks/tasks-page";
import { mockSprintTasks } from "@/lib/tasks/mock-data";

export default function Page() {
  return <TasksPage tasks={mockSprintTasks} />;
}
