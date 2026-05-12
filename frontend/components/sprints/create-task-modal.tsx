"use client";

import { useMemo, useState } from "react";
import type { CreateTaskInput, SprintMember } from "@/lib/sprints/types";

type CreateTaskModalProps = {
  open: boolean;
  members: SprintMember[];
  onClose: () => void;
  onCreate: (input: CreateTaskInput) => void;
};

const initialForm: CreateTaskInput = {
  title: "",
  priority: "medium",
  status: "todo",
  dueDate: "",
  storyPoints: 3,
  tags: [],
  assigneeIds: [],
};

export function CreateTaskModal({ open, members, onClose, onCreate }: CreateTaskModalProps) {
  const [form, setForm] = useState<CreateTaskInput>(initialForm);
  const [tagInput, setTagInput] = useState("");

  const canSubmit = useMemo(
    () => form.title.trim().length >= 3 && form.dueDate.length > 0,
    [form.dueDate, form.title],
  );

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/45 p-4">
      <div className="w-full max-w-[560px] rounded-3xl border border-[#d8ddf1] bg-white p-6 shadow-[0_24px_60px_rgba(15,23,42,0.24)]">
        <header className="mb-5 flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-800">Create Task</h2>
            <p className="mt-1 text-sm text-slate-500">Add a new issue to the active sprint board.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-slate-500 hover:bg-slate-100"
            aria-label="Close modal"
          >
            ✕
          </button>
        </header>

        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            if (!canSubmit) {
              return;
            }
            onCreate(form);
            setForm(initialForm);
            setTagInput("");
            onClose();
          }}
        >
          <label className="block space-y-1">
            <span className="text-sm font-semibold text-slate-700">Task title</span>
            <input
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              placeholder="Ex: Improve cache eviction policy"
            />
          </label>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-slate-700">Priority</span>
              <select
                value={form.priority}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    priority: event.target.value as CreateTaskInput["priority"],
                  }))
                }
                className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>

            <label className="block space-y-1">
              <span className="text-sm font-semibold text-slate-700">Status</span>
              <select
                value={form.status}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    status: event.target.value as CreateTaskInput["status"],
                  }))
                }
                className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              >
                <option value="todo">Todo</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            </label>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-slate-700">Due date</span>
              <input
                type="date"
                value={form.dueDate}
                onChange={(event) => setForm((current) => ({ ...current, dueDate: event.target.value }))}
                className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              />
            </label>
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-slate-700">Story points</span>
              <input
                type="number"
                min={1}
                max={21}
                value={form.storyPoints}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    storyPoints: Number(event.target.value) || 1,
                  }))
                }
                className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              />
            </label>
          </div>

          <label className="block space-y-1">
            <span className="text-sm font-semibold text-slate-700">Tags (comma separated)</span>
            <input
              value={tagInput}
              onChange={(event) => setTagInput(event.target.value)}
              onBlur={() =>
                setForm((current) => ({
                  ...current,
                  tags: tagInput
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
                }))
              }
              className="h-11 w-full rounded-xl border border-slate-200 px-3 text-[15px] text-slate-700 focus:border-[#4f46e5] focus:outline-none"
              placeholder="Backend, API"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-slate-700">Assignees</span>
            <div className="grid grid-cols-2 gap-2">
              {members.map((member) => (
                <label key={member.id} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600">
                  <input
                    type="checkbox"
                    checked={form.assigneeIds.includes(member.id)}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        assigneeIds: event.target.checked
                          ? [...current.assigneeIds, member.id]
                          : current.assigneeIds.filter((id) => id !== member.id),
                      }))
                    }
                  />
                  {member.name}
                </label>
              ))}
            </div>
          </label>

          <div className="mt-2 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!canSubmit}
              className="rounded-xl bg-[#3f2fd6] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

